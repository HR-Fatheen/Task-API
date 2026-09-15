from supabase_auth.errors import AuthApiError
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from supabase_client import supabase
from database import get_connection
from psycopg.rows import dict_row
from pydantic import BaseModel

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Server running and connected to Supabase")
    yield

app = FastAPI(lifespan=lifespan)


class CreateTask(BaseModel):
    title: str | None = None


class UpdateTask(BaseModel):
    title: str
    done: bool

class AuthRequest(BaseModel):
    email: str | None = None
    password: str | None = None

@app.post("/auth/signup", status_code=201)
def signup(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    response = supabase.auth.sign_up({
        "email": auth.email,
        "password": auth.password
    })

    return response.user

@app.post("/auth/login")
def login(auth: AuthRequest):
    if not auth.email or not auth.password:
        raise HTTPException(
            status_code=400,
            detail="Email and password are required"
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": auth.email,
            "password": auth.password
        })

        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token
        }

    except AuthApiError:
        return JSONResponse(
            status_code=401,
            content={"error": "Invalid login credentials"}
        )

@app.get("/", summary="API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Health check")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks", summary="List all tasks")
def task_manager():
    connection = get_connection()
    connection.row_factory = dict_row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return tasks


@app.get("/tasks/{id}", summary="Get a task by ID")
def get_task(id: int):
    connection = get_connection()
    connection.row_factory = dict_row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (id,))
    task = cursor.fetchone()

    cursor.close()
    connection.close()

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.post("/tasks", summary="Create a new task", status_code=201)
def create_task(task: CreateTask):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    connection = get_connection()
    connection.row_factory = dict_row
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, done)
        VALUES (%s, %s)
        RETURNING id, title, done
    """, (task.title.strip(), False))

    new_task = cursor.fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    return new_task

@app.put("/tasks/{id}", summary="Update a task")
def update_task(id: int, task: UpdateTask):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")

    connection = get_connection()
    connection.row_factory = dict_row
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = %s, done = %s
        WHERE id = %s
        RETURNING id, title, done
    """, (task.title.strip(), task.done, id))

    updated_task = cursor.fetchone()

    if updated_task is None:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()
    cursor.close()
    connection.close()

    return updated_task


@app.delete("/tasks/{id}", summary="Delete a task", status_code=204)
def delete_task(id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = %s
    """, (id,))

    if cursor.rowcount == 0:
        connection.close()
        raise HTTPException(status_code=404, detail="Task not found")

    connection.commit()
    cursor.close()
    connection.close()