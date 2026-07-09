# 🚀 High-Performance FastAPI Application

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge)](https://docs.pydantic.dev)

🚀 High-performance, production-ready FastAPI application built with modern backend practices. Features robust data validation via Pydantic, automated OpenAPI documentation, structured error handling, and optimized endpoints. Scalable, secure, and ready for frontend integration.

---

## ✨ Features

- **Robust Authentication:** Secure user authentication and state management.
- **Data Validation:** Strict and fast request/response validation utilizing Pydantic.
- **Database Migrations:** Clean schema management powered by Alembic.
- **Automated Docs:** Instant, interactive API documentation via Swagger UI and ReDoc.
- **Testing Suite:** Comprehensive unit tests implemented using Pytest.

---

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.12
- **Validation & Settings:** Pydantic v2
- **Database (ORM):** SQLAlchemy
- **Migration:** Alembic
- **Testing:** Pytest

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have Python 3.12+ installed on your system.

### 2. Installation
Clone the repository and navigate into the project directory:
```bash
git clone <https://github.com/EnesAytekintr/request_management_system_with_FastAPI.git>
cd FastAPI2

### 3. Environment Variables
Create a `.env` file in the root directory based on `.env.example` and fill in your local PostgreSQL credentials.

### 4. Database Migrations
Run the following command to generate the database schema automatically via Alembic:
```bash
alembic upgrade head