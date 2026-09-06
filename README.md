# Task API

A lightweight **RESTful Task Management API** built with **Python** and **FastAPI**.

The API supports the complete CRUD lifecycle for tasks — creating, retrieving, updating, and deleting tasks — with input validation and appropriate HTTP status codes.

## Features

* RESTful API built with FastAPI
* Complete CRUD operations
* Pydantic request validation
* Automatic Swagger/OpenAPI documentation
* Proper HTTP status codes
* In-memory task storage
* Error handling for invalid titles and missing tasks

## Tech Stack

| Technology        | Purpose                       |
| ----------------- | ----------------------------- |
| Python 3.10+      | Programming language          |
| FastAPI           | Web framework                 |
| Pydantic          | Request validation            |
| Uvicorn           | ASGI server                   |
| Swagger / OpenAPI | Interactive API documentation |

## Getting Started

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd <repository-folder>
```

### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install fastapi uvicorn
```

### 4. Start the server

```powershell
python -m uvicorn main:app --reload
```

The API will be available at:

`http://localhost:8000`

## API Documentation

FastAPI automatically generates interactive Swagger documentation.

Open:

`http://localhost:8000/docs`

From Swagger UI, you can execute and test all API endpoints directly from your browser.

## API Endpoints

|  Method  | Endpoint      | Description                   |
| :------: | ------------- | ----------------------------- |
|   `GET`  | `/`           | Returns API information       |
|   `GET`  | `/health`     | Returns the API health status |
|   `GET`  | `/tasks`      | Returns all tasks             |
|   `GET`  | `/tasks/{id}` | Returns a task by ID          |
|  `POST`  | `/tasks`      | Creates a new task            |
|   `PUT`  | `/tasks/{id}` | Updates an existing task      |
| `DELETE` | `/tasks/{id}` | Deletes a task                |

## Request Examples

### Create a Task

**POST `/tasks`**

```json
{
  "title": "Buy Milk"
}
```

Successful response:

```json
{
  "id": 4,
  "title": "Buy Milk",
  "done": false
}
```

### Update a Task

**PUT `/tasks/{id}`**

```json
{
  "title": "Buy Groceries",
  "done": true
}
```

Successful response:

```json
{
  "id": 4,
  "title": "Buy Groceries",
  "done": true
}
```

### Delete a Task

**DELETE `/tasks/{id}`**

Successful response:

```json
{
  "message": "Task deleted"
}
```

## HTTP Status Codes

|         Status Code        | Meaning                                    |
| :------------------------: | ------------------------------------------ |
|          `200 OK`          | Request completed successfully             |
|        `201 Created`       | A new task was created                     |
|      `400 Bad Request`     | Task title is missing or empty             |
|       `404 Not Found`      | Requested task does not exist              |
| `422 Unprocessable Entity` | Request body contains invalid JSON or data |

## Data Storage

This project currently uses **in-memory storage**.

Tasks are stored in a Python list while the server is running. Restarting the server resets the task data to the initial list.

## Project Structure

```text
Assignment 1/
│
├── main.py
├── README.md
├── .gitignore
└── .venv/
```

## Swagger UI

The API was tested using FastAPI's built-in Swagger UI, including the complete CRUD workflow:

**Create → Read → Update → Delete**

*Add your Swagger UI screenshot below.*

![Swagger UI](swagger-screenshot.png)

## Project Status

**Stage 6 — Documentation & Publishing**

The API implements the complete CRUD workflow and includes interactive Swagger documentation.
