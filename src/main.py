import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from sql_queries import generate_sql_query, execute_sql_query, explain_results
from caching import set_cache, get_repsonse, redis_server

app = FastAPI()

# Initialize FAISS
embedding_dim = 384
faiss_index = faiss.IndexFlatL2(embedding_dim)
model = SentenceTransformer("all-MiniLM-L6-v2")

# In-memory store
query_db = {}
query_embeddings = np.empty((0, embedding_dim), dtype=np.float32)

# Define Request Schema
class QueryRequest(BaseModel):
    user_query: str


@app.post("/query")
def handle_query(request: QueryRequest):
    user_query = request.user_query

    # 1. Check Redis
    if redis_server.exists(user_query):
        response = get_repsonse(user_query)
        return {
            "cached": True,
            "sql_query": response["sql_query"],
            "records": response["records"][:5],
            "explanation": response["explanation"]
        }

    # 2. FAISS semantic similarity check
    user_embedding = model.encode([user_query]).astype(np.float32)
    if faiss_index.ntotal > 0:
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

    # 3. Generate + run query
    try:
        sql_query = generate_sql_query(user_query)
        records = execute_sql_query(sql_query)
        explanation = explain_results(user_query, records)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. Cache result
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
    uvicorn.run(app, host="0.0.0.0", port=80)
