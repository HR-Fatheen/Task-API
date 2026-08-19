from fastapi import FastAPI , HTTPException

app = FastAPI()

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