# Task API

A lightweight RESTful Task Management API built with Python and FastAPI.

The project started as an in-memory Task API and was progressively migrated to SQLite, then PostgreSQL, and finally containerized using Docker Compose.

## Features

* RESTful API built with FastAPI
* Complete CRUD operations for tasks
* Pydantic request validation
* PostgreSQL database storage
* Parameterized SQL queries
* Automatic database and table creation
* Initial task seeding
* Proper HTTP status codes
* Error handling for invalid titles and missing tasks
* Automatic Swagger/OpenAPI documentation
* Supabase Authentication
* JWT access token verification
* Protected API routes
* Reusable authentication dependency
* Swagger Bearer authentication
* Login and signup endpoints
* Logout endpoint
* Dockerized FastAPI application
* Dockerized PostgreSQL database
* Persistent PostgreSQL storage using a named Docker volume
* One-command startup using Docker Compose

## Tech Stack

| Technology        | Purpose                             |
| ----------------- | ----------------------------------- |
| Python 3.12       | Programming language                |
| FastAPI           | Web framework                       |
| Pydantic          | Request validation                  |
| Uvicorn           | ASGI server                         |
| PostgreSQL 16     | Database                            |
| Psycopg           | PostgreSQL database driver          |
| Docker            | Application and database containers |
| Docker Compose    | Multi-container orchestration       |
| Swagger / OpenAPI | Interactive API documentation       |
| Supabase          | Authentication and user management  |
| JWT               | Access token authentication         |

## Getting Started

### Prerequisites

Make sure the following are installed:

* Python 3.12+
* Docker Desktop
* Git

### 1. Clone the repository

```powershell
git clone https://github.com/HR-Fatheen/Task-API.git
cd Task-API
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
POSTGRES_PASSWORD=your_password_here
POSTGRES_DB=tasks
DATABASE_URL=postgres://postgres:your_password_here@localhost:5432/tasks
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_or_publishable_key
PORT=8000
```

The `.env` file is excluded from Git using `.gitignore`.

A `.env.example` file is included in the repository as a configuration reference.

For Supabase authentication, set `SUPABASE_URL` and `SUPABASE_KEY` using the values from your Supabase project.

Never commit `.env` or expose Supabase credentials in the repository.

### 3. Start the application

Build and start the complete application stack using Docker Compose:

```powershell
docker compose up --build
```

This starts:

* FastAPI application
* PostgreSQL database

The API will be available at:

```text
http://localhost:8000
```

### 4. Stop the application

To stop the containers:

```powershell
docker compose down
```

The PostgreSQL data remains stored in the named Docker volume.

To start the application again:

```powershell
docker compose up
```

## API Documentation

FastAPI automatically generates interactive Swagger/OpenAPI documentation.

Open:

```text
http://localhost:8000/docs
```

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
| `POST`   | `/auth/signup`| Creates a new user account    |
| `POST`   | `/auth/login` | Authenticates a user and returns access/refresh tokens |
| `POST`   | `/auth/logout`|Logs out the authenticated user|
| `GET`    | `/public/info`| Public information endpoint   |
| `GET`    |`/protected/profile` |Returns authenticated user information |
| `GET`    |`/protected/status` |Verifies that the request is authenticated|

## Authentication

The API uses Supabase Authentication with JWT access tokens.

### Signup

Create a new user account using:

`POST /auth/signup`

Example request:

```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

### Login

Authenticate an existing user using:
```json
POST /auth/login
```

A successful login returns an access token and refresh token.

The access token must be included when calling protected endpoints:
```text
Authorization: Bearer <access_token>
```

### Protected Routes

The following routes require a valid access token:
```text
GET /protected/profile
GET /protected/status
POST /auth/logout
```

Requests without a token return:
```json
{
  "error": "Access token required"
}
```

Invalid or expired tokens return:
```json
{
  "error": "Invalid or expired token"
}
```

### Swagger Authentication

Swagger UI supports Bearer authentication.

Open:
```json
http://localhost:8000/docs
```

Click Authorize, enter the access token, and then execute the protected endpoints.

## Request Examples

### Create a Task

**POST `/tasks`**

```json
{
  "title": "Buy Milk"
}
```

Example successful response:

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

Example successful response:

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

```text
204 No Content
```

The DELETE endpoint does not return a response body when the task is successfully deleted.

## HTTP Status Codes

|         Status Code        | Meaning                            |
| :------------------------: | ---------------------------------- |
|          `200 OK`          | Request completed successfully     |
|        `201 Created`       | A new task was created             |
|      `204 No Content`      | Task was successfully deleted      |
|      `400 Bad Request`     | Task title is missing or empty     |
|       `404 Not Found`      | Requested task does not exist      |
| `422 Unprocessable Entity` | Request body contains invalid data |
| `401 Unauthorized` | Missing, invalid, or expired authentication token |

## Authentication Flow

The authentication flow is:

1. User signs up using `/auth/signup`.
2. User logs in using `/auth/login`.
3. Supabase returns an access token and refresh token.
4. The client sends the access token using the `Authorization` header.
5. Protected routes verify the JWT through Supabase.
6. Invalid or expired tokens are rejected with `401 Unauthorized`.

Authentication is implemented using a reusable FastAPI dependency, which is shared by the protected routes.

## PostgreSQL Database

The application uses PostgreSQL 16 for persistent task storage.

PostgreSQL runs inside its own Docker container and is accessed by the FastAPI container using the Docker Compose service name:

```text
db
```

The API container connects to PostgreSQL using:

```text
postgres://postgres:<password>@db:5432/<database>
```

The database and `tasks` table are created automatically when the API starts.

If the table is empty, the application seeds it with three example tasks:

```text
Learn Python
Test The Product
Configure The DB
```

All CRUD operations use parameterized PostgreSQL queries.

## Docker Architecture

```text
                    Docker Compose
                         |
              +----------+----------+
              |                     |
              v                     v
        +-----------+        +-------------+
        |    API    |        | PostgreSQL  |
        |  FastAPI  | -----> |     db      |
        |   :8000   |        |    :5432    |
        +-----------+        +-------------+
                                    |
                                    v
                             taskdata volume
```

The API communicates with PostgreSQL through the Docker Compose service name `db`.

The PostgreSQL data is stored in a named Docker volume so that task data persists when the containers are stopped and started again.

## Docker Persistence Test

To verify database persistence:

### 1. Start the application

```powershell
docker compose up --build
```

### 2. Create a task

```powershell
Invoke-RestMethod -Method Post `
    -Uri "http://127.0.0.1:8000/tasks" `
    -ContentType "application/json" `
    -Body '{"title":"Running in Docker"}'
```

### 3. Stop the containers

```powershell
docker compose down
```

### 4. Start the application again

```powershell
docker compose up
```

### 5. Retrieve the tasks

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/tasks"
```

The previously created task remains in the database because PostgreSQL data is stored in the named Docker volume.

## Testing with curl

### Get all tasks

```powershell
curl.exe -i http://127.0.0.1:8000/tasks
```

### Create a task

```powershell
curl.exe -i -X POST http://127.0.0.1:8000/tasks `
    -H "Content-Type: application/json" `
    -d '{"title":"Test Task"}'
```

### Get a task

```powershell
curl.exe -i http://127.0.0.1:8000/tasks/1
```

### Update a task

```powershell
curl.exe -i -X PUT http://127.0.0.1:8000/tasks/1 `
    -H "Content-Type: application/json" `
    -d '{"title":"Updated Task","done":true}'
```

### Delete a task

```powershell
curl.exe -i -X DELETE http://127.0.0.1:8000/tasks/1
```

## Project Structure

```text
Task-API/
│
├── main.py
├── database.py
├── supabase_client.py
├── requirements.txt
├── Dockerfile
├── compose.yaml
├── .dockerignore
├── .env.example
├── .gitignore
├── README.md
├── postgresql-screenshot.png
└── swagger-screenshot.png
```

## Assignment Progress

### Assignment 1 — In-Memory Task API

The initial API implemented the basic task management endpoints using in-memory data.

### Assignment 2 — SQLite Database Migration

The API was migrated from in-memory storage to SQLite, implementing persistent CRUD operations.

### Assignment 3 — PostgreSQL and Docker

The application was migrated from SQLite to PostgreSQL and containerized using Docker.

The final implementation includes:

* PostgreSQL running in Docker
* FastAPI connected to PostgreSQL
* Full PostgreSQL CRUD operations
* Dockerized FastAPI application
* Dockerized PostgreSQL database
* Docker Compose configuration
* Persistent named Docker volume
* Environment-based database configuration
* One-command application startup
* Swagger/OpenAPI documentation
* Appropriate HTTP status codes
* Input validation
* Persistent data across container restarts

### Assignment 4 — Supabase Authentication

The API was secured using Supabase Authentication and JWT access tokens.

The implementation includes:

* Supabase Authentication setup
* User signup and login
* JWT access token verification
* Protected API routes
* Reusable authentication dependency
* Authenticated logout endpoint
* Swagger Bearer authentication
* Public and protected endpoints
* Authentication error handling

## PostgreSQL Database Verification

PostgreSQL was verified using `psql` inside the PostgreSQL Docker container.

The database contains the `tasks` table and the seeded task records.

![PostgreSQL Database](postgresql-screenshot.png)

## Swagger UI

The API was tested using FastAPI's built-in Swagger UI.

Swagger UI supports Bearer authentication for protected endpoints. Use the **Authorize** button to provide a valid access token.

The complete CRUD workflow was also tested:

**Create → Read → Update → Delete**

![Swagger UI](swagger-screenshot.png)

## Project Status

**Assignment 4 — FastAPI + PostgreSQL + Supabase Authentication**

The Task API is fully containerized using Docker Compose and secured using Supabase Authentication.

The complete stack can be started with:

```powershell
docker compose up --build
```

API:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/docs
```

The PostgreSQL database uses a named Docker volume, allowing task data to persist across container restarts.
