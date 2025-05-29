import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sql_queries import generate_sql_query, execute_sql_query, explain_results
from caching import set_cache, get_repsonse, redis_server
from prometheus_client import (
    Counter, Summary, generate_latest, CONTENT_TYPE_LATEST
)

app = FastAPI()

# Initialize FAISS
embedding_dim = 384
faiss_index = faiss.IndexFlatL2(embedding_dim)
model = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory store
query_db = {}
query_embeddings = np.empty((0, embedding_dim), dtype=np.float32)

# Prometheus Metrics
api_calls_total = Counter("api_calls_total", "Total number of API calls", ["method", "endpoint"])
api_responses_total = Counter("api_responses_total", "HTTP responses by status code", ["status_code"])
api_errors_total = Counter("api_errors_total", "Total number of exceptions", ["exception"])
request_latency = Summary("request_latency_seconds", "Request latency in seconds", ["endpoint"])

redis_hits = Counter("redis_hits_total", "Number of Redis cache hits")
redis_misses = Counter("redis_misses_total", "Number of Redis cache misses")

faiss_queries_total = Counter("faiss_queries_total", "Total number of FAISS similarity searches")
sql_exec_time = Summary("sql_execution_time_seconds", "SQL query execution time")

# Middleware for Prometheus metrics
@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    api_calls_total.labels(method=method, endpoint=endpoint).inc()

    with request_latency.labels(endpoint=endpoint).time():
        try:
            response = await call_next(request)
            api_responses_total.labels(status_code=response.status_code).inc()
            return response
        except Exception as e:
            api_errors_total.labels(exception=type(e).__name__).inc()
            raise e


# Schema
class QueryRequest(BaseModel):
    user_query: str

@app.get("/")
def root():
    return {"message": "Welcome to the Hotel Booking Query API. Use /query to submit your SQL queries."}

# Metrics Endpoint for Prometheus scraping
@app.get("/metrics")
def get_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# Main Endpoint
@app.post("/query")
def handle_query(request: QueryRequest):
    user_query = request.user_query

    # Check Redis
    if redis_server.exists(user_query):
        redis_hits.inc()
        response = get_repsonse(user_query)
        return {
            "cached": True,
            "sql_query": response["sql_query"],
            "records": response["records"][:5],
            "explanation": response["explanation"]
        }

    redis_misses.inc()

    # FAISS semantic similarity
    user_embedding = model.encode([user_query]).astype(np.float32)
    if faiss_index.ntotal > 0:
        faiss_queries_total.inc()
        D, I = faiss_index.search(user_embedding, 1)
        similarity_score = 1 - D[0][0]
        best_match_idx = I[0][0]

        if similarity_score > 0.99 and best_match_idx < len(query_db):
            matched_query = list(query_db.keys())[best_match_idx]
            cached = query_db[matched_query]
            return {
                "cached": True,
                "sql_query": cached["sql_query"],
                "records": cached["records"][:5],
                "explanation": cached["explanation"]
            }

    # Generate SQL and Execute
    try:
        sql_query = generate_sql_query(user_query)
        with sql_exec_time.time():
            records = execute_sql_query(sql_query)
        explanation = explain_results(user_query, records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Cache result
    cache_obj = {
        "sql_query": sql_query,
        "records": records,
        "explanation": explanation
    }
    set_cache(user_query, cache_obj)
    query_db[user_query] = cache_obj
    global query_embeddings
    query_embeddings = np.vstack((query_embeddings, user_embedding))
    faiss_index.add(user_embedding)

    return {
        "cached": False,
        "sql_query": sql_query,
        "records": records[:5],
        "explanation": explanation
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
