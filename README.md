# Resilient Decision System

A highly configurable workflow decision platform built for the hackathon. It evaluates incoming requests against business rules, manages state, handles external dependency failures, ensures idempotency, and maintains a strict audit trail.

## Tech Stack
* Python 3.10+
* FastAPI (API routing and Swagger UI)
* Pydantic (Input schema validation)
* SQLite & SQLAlchemy (State management and Audit logs)
* Pytest (Automated testing)

## How to Run the Application

1. **Activate Virtual Environment:**
   * Windows: `venv\Scripts\activate`
    

2. **Install Dependencies:**
   ```bash
   pip install fastapi uvicorn sqlalchemy pydantic pytest httpx