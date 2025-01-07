from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
import httpx
from pydantic import BaseModel
from typing import Optional

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DJANGO_API_URL = "http://127.0.0.1:8001/" 

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

@app.post("/start_task/")
async def start_task_endpoint(task_request: AnalyzePRRequest):
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{DJANGO_API_URL}/start_task/",
            data={
                "repo_url": task_request.repo_url,
                "pr_number": task_request.pr_number,
                "github_token": task_request.github_token,

            }
        )
        if response.status_code != 200:
            return {"error": "Failed to start task", "details": response.text}
        task_id = response.json().get("task_id")
        return {"task_id": task_id, "status": "Task started"}

@app.get("/task_status/{task_id}/")
async def task_status_endpoint(task_id: str):
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/task_status_view/{task_id}/")
        print(response)
        return response.json()
    
    return {"message": "something went wrong",}

@app.get("/task_result/{task_id}/")
async def task_status_endpoint(task_id: str):
    
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}/task_result_view/{task_id}/")
        print(response)
        return response.json()
    
    return {"message": "something went wrong",}