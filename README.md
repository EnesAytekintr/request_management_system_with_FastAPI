# 🚀 High-Performance FastAPI Application

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge)](https://docs.pydantic.dev)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com)

🚀 High-performance, production-ready FastAPI application built with modern backend practices. Features robust data validation via Pydantic, automated OpenAPI documentation, structured error handling, and optimized endpoints. Scalable, secure, and ready for frontend integration.

---

## ✨ Features

- **Robust Authentication:** Secure user authentication and state management.
- **Data Validation:** Strict and fast request/response validation utilizing Pydantic.
- **Database Migrations:** Clean schema management powered by Alembic.
- **Automated Docs:** Instant, interactive API documentation via Swagger UI and ReDoc.
- **Testing Suite:** Comprehensive unit tests implemented using Pytest.

---

## 📐 Design Choices & Architecture

This project is architected with a strong focus on high scalability, lightweight infrastructure, and secure deployment pipelines. Below are the key design patterns and infrastructure choices:

### 1. Asynchronous Infrastructure & ORM
- Built entirely on **Asynchronous Python (FastAPI + Asyncpg)** to unlock maximum throughput and non-blocking I/O operations.
- Database access is managed via **SQLAlchemy (Async Session)** paired with connection pooling mechanics to optimally communicate with cloud/local relational databases without blocking worker threads.

### 2. Lightweight & Optimized Containerization (Docker)
- **Base OS Selection:** Switched to `python:3.12-slim` to maintain a robust yet ultra-lightweight (~77MB) production image footprint, dropping bulkier standard distributions while avoiding potential Alpine-compilation complexities.
- **Advanced Layer Caching:** Implemented cache mounts (`--mount=type=cache,target=/root/.cache/pip`) inside the `Dockerfile`. This keeps heavy `pip install` layers isolated; if `requirements.txt` remains unchanged, Docker bypasses dependency installation entirely during sequential builds, slicing compilation time down to milliseconds.
- **Dependency Cleansing:** Rigidly audited and trimmed down `requirements.txt`, eliminating bloated and unused temporary dependencies to shrink the total target container context.
- **Context Isolation:** Deployed a strict `.dockerignore` scheme to fully isolate runtime files, local virtual environments (`.venv`), temporary test caches (`__pycache__`, `.pytest_cache`), and `.git` data from leaking into the container layers.

### 3. Zero-Leak Security & Configuration Management
- **Runtime Environment Injection:** No cryptographic tokens, administrative passwords, algorithms, or database URLs are baked into the Docker image layers. The image remains completely "blind" and stateless.
- **Isolation Boundaries:** Sensitive credentials exist exclusively on the local host machine within an uncommitted `.env` file (strictly guarded by `.gitignore`). Docker Compose safely enjects these parameters directly into the container's RAM space during runtime initialization via `env_file`, neutralizing accidental exposure on GitHub or container registry scanning.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12 (Asynchronous)
- **Validation & Settings:** Pydantic v2
- **Database (ORM):** SQLAlchemy (Asyncpg)
- **Migration:** Alembic
- **Testing:** Pytest
- **Containerization:** Docker & Docker Compose

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have **Docker** and **Docker Compose** installed on your system.

### 2. Installation
Clone the repository and navigate into the project directory:
```bash
git clone [https://github.com/EnesAytekintr/request_management_system_with_FastAPI.git](https://github.com/EnesAytekintr/request_management_system_with_FastAPI.git)
cd FastAPI2
```
### 3. Environment Setup
Create a .env file in the root directory based on .env.example and fill in your cloud (e.g., Neon) or local PostgreSQL credentials:

DATABASE_URL=postgresql+asyncpg://user:password@host:port/dbname
SECRET_KEY=your_super_secret_key
ALGORITHM=HS256

### 4. Running the Application via Docker Compose (Recommended)
You can compile the optimized image and orchestrate the live container container in detached mode with a single command:

```bash
docker compose up -d --build
```
The application will automatically initialize, bind the environment, set up active volume syncing for instant hot-reloads, and map the worker gateway.

API Documentation: http://localhost:8000/docs (Swagger UI)

Live Stream Logs: docker logs -f api-server

Tear Down Infrastructure: docker compose down

### 5. Database Migrations
To stream up-to-date relational schemas or trigger Alembic migrations directly inside the running isolated container ecosystem, execute:

```bash
docker exec -it api-server alembic upgrade head
```
