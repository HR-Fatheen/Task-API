from fastapi import FastAPI , HTTPException
from database import get_connection
from pydantic import BaseModel

app = FastAPI()

class CreateTask(BaseModel):
    title:str | None = None

@app.get("/", summary="API information")
def root():
    return {
        "name" : "Task API",
        "version" : "1.0",
        "endpoints" : ["/tasks"]
    }

@app.get("/health", summary="Health check")
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

@app.get("/tasks", summary="List all tasks")
def task_manager():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    connection.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{id}", summary="Get a task by ID")
def get_task(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id,))
    task = cursor.fetchone()
    connection.close()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return dict(task)

@app.post("/tasks", summary="Create a new task", status_code=201)
def create_task(task: CreateTask):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, done)
        VALUES (?,?)
    """, (task.title.strip(), False))
    new_id = cursor.lastrowid
    connection.commit()
    connection.close()

    return{
        "id": new_id,
        "title": task.title.strip(),
        "done": False
    }

class UpdateTask(BaseModel):
    title: str
    done: bool

@app.put("/tasks/{id}", summary="Update a task")
def update_task(id: int, task: UpdateTask):
    for existing_task in tasks:
        if existing_task["id"] == id:
            if not task.title.strip():
                raise HTTPException(status_code=400, detail="Title is required")

            existing_task["title"] = task.title
            existing_task["done"] = task.done

            return existing_task

    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{id}", summary="Delete a task")
def delete_task(id: int):
    for task in tasks:
        if task["id"] == id:
            tasks.remove(task)
            return {"message": "Task deleted"}

    raise HTTPException(status_code=404, detail="Task not found")