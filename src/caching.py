import redis 
import json 
import os
try : 
    redis_server = redis.StrictRedis(
    host=os.getenv("REDIS_HOST", "redis-service"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0
)


    def set_cache(query, response) : 

        redis_server.set(query, json.dumps(response))

    def get_repsonse(query) : 

        response =  redis_server.get(query)

        if response : 

            return json.loads(response.decode('utf-8')) 
        
        return "didnt find anything in cache"



except redis.exceptions.ConnectionError as e:
    print(f"Redis connection error: {e}")
    redis_server = None  # Set to None if connection fails

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    redis_server = None  # Set to None if any other error occurs    