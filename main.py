from groq_connector import get_groq_response
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import uuid
import uvicorn

app = FastAPI(
    title="Task Manager API",
    description="Task manager endpoints plus Groq chat endpoint",
    version="1.0.0",
)


class ChatRequest(BaseModel):
    prompt: str


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_completed: bool = False


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: str
    created_at: datetime
    updated_at: datetime


tasks_db: Dict[str, Task] = {}


def get_task_or_404(task_id: str) -> Task:
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with ID {task_id} not found",
        )
    return task


@app.get("/")
def health():
    return {
        "message": "Welcome to the Task Manager API",
        "docs": "/docs",
        "tasks_endpoint": "/tasks",
        "chat_endpoint": "/chat",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return list(tasks_db.values())


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    task_id = str(uuid.uuid4())
    current_time = datetime.now()
    new_task = Task(
        id=task_id,
        created_at=current_time,
        updated_at=current_time,
        **task.model_dump(),
    )
    tasks_db[task_id] = new_task
    return new_task


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    return get_task_or_404(task_id)


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskCreate):
    task = get_task_or_404(task_id)
    for key, value in task_update.model_dump().items():
        setattr(task, key, value)
    task.updated_at = datetime.now()
    tasks_db[task_id] = task
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str):
    get_task_or_404(task_id)
    del tasks_db[task_id]
    return None


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        response = get_groq_response(request.prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc
    return {"response": response}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
