from fastapi import FastAPI , HTTPException
from pydantic import BaseModel

app = FastAPI()

class CreateTask(BaseModel):
    title:str | None = None

@app.get("/")
def root():
    return {
        "name" : "Task API",
        "version" : "1.0",
        "endpoints" : ["/tasks"]
    }

@app.get("/health")
def health():
    return {
        "status" : "ok"
    }

tasks = [
    {
        "id": 1,
        "title": "Learn Python",
        "done": False
    },
    {
        "id": 3,
        "title": "Test The Product",
        "done": False
    },
    {
        "id": 2,
        "title": "Configure The DB",
        "done": False
    }
]

@app.get("/tasks")
def task_manager():
    return tasks

@app.get("/tasks/{id}")
def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", status_code=201)
def create_task(task: CreateTask):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    max_id = max(tasks, key=lambda task: task["id"])["id"]
    new_id = max_id + 1

    new_task = {
        "id":new_id,
        "title":task.title,
        "done":False
    }

    tasks.append(new_task)
    return new_task

class UpdateTask(BaseModel):
    title: str
    done: bool

@app.put("/tasks/{id}")
def update_task(id: int, task: UpdateTask):
    for existing_task in tasks:
        if existing_task["id"] == id:
            if not task.title.strip():
                raise HTTPException(status_code=400, detail="Title is required")

            existing_task["title"] = task.title
            existing_task["done"] = task.done

            return existing_task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{id}")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")