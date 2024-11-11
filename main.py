import logging
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from celery.result import AsyncResult
from celery_app import analyze_pr_task 
import uvicorn
import redis
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler 
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

# structured logging
logging.basicConfig(level=logging.INFO, format='{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
logger = logging.getLogger(__name__)

app = FastAPI()

# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # Updated line
app.add_middleware(SlowAPIMiddleware)

# Redis for caching
redis_client = redis.Redis(host="localhost", port=6379, db=1)

class PRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None 

@app.post("/analyze-pr")
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute per client IP
async def analyze_pr(pr_request: PRRequest, request: Request):
    cache_key = f"pr:{pr_request.repo_url}:{pr_request.pr_number}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        logger.info("Returning cached result", extra={"cache_key": cache_key})
        return {"task_id": "cached", "results": json.loads(cached_result)}
    
    try:
        logger.info("Starting new task", extra={"repo_url": pr_request.repo_url, "pr_number": pr_request.pr_number})
        task = analyze_pr_task.apply_async(args=[pr_request.repo_url, pr_request.pr_number, pr_request.github_token])
        redis_client.setex(cache_key, 3600, json.dumps({"task_id": task.id}))

        return {"task_id": task.id}
    except Exception as e:
        logger.error("Error in analyze_pr", exc_info=True, extra={"repo_url": pr_request.repo_url, "pr_number": pr_request.pr_number})
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{task_id}")
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute per client IP
async def get_task_status(task_id: str, request: Request):
    task_result = AsyncResult(task_id)
    logger.info("Fetching task status", extra={"task_id": task_id, "status": task_result.status})
    return {"task_id": task_id, "status": task_result.status}


@app.get("/results/{task_id}")
@limiter.limit("5/minute")  # Rate limit: 5 requests per minute per client IP
async def get_task_results(task_id: str, request: Request):
    task_result = AsyncResult(task_id)

    if task_result.status == "SUCCESS":
        result = task_result.result
        cache_key = f"task:{task_id}"
        redis_client.setex(cache_key, 3600, json.dumps(result))
        logger.info("Task completed successfully", extra={"task_id": task_id})
        return {"task_id": task_id, "status": "completed", "results": result}
    
    elif task_result.status == "PENDING":
        logger.info("Task is pending", extra={"task_id": task_id})
        return {"task_id": task_id, "status": "pending"}
    
    elif task_result.status == "FAILURE":
        logger.error("Task failed", extra={"task_id": task_id, "error": str(task_result.result)})
        return {"task_id": task_id, "status": "failed", "error": str(task_result.result)}
    
    else:
        logger.info("Task status unknown", extra={"task_id": task_id, "status": task_result.status})
        return {"task_id": task_id, "status": task_result.status}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
