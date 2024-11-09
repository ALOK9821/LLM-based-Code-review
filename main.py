from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from celery.result import AsyncResult
from celery_app import analyze_pr_task 
import uvicorn

app = FastAPI()

class PRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None 

@app.post("/analyze-pr")
async def analyze_pr(pr_request: PRRequest):
    try:
        task = analyze_pr_task.apply_async(args=[pr_request.repo_url, pr_request.pr_number, pr_request.github_token])

        return {"task_id": task.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{task_id}")
async def get_task_status(task_id: str):
    task_result = AsyncResult(task_id)
    return {"task_id": task_id, "status": task_result.status}


@app.get("/results/{task_id}")
async def get_task_results(task_id: str):
    task_result = AsyncResult(task_id)

    if task_result.status == "SUCCESS":
        return {"task_id": task_id, "status": "completed", "results": task_result.result}
    elif task_result.status == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    elif task_result.status == "FAILURE":
        return {"task_id": task_id, "status": "failed", "error": str(task_result.result)}
    else:
        return {"task_id": task_id, "status": task_result.status}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
