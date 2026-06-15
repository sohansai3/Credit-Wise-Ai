import os
import tempfile

import pytest
from fastapi.testclient import TestClient

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["MODEL_PATH"] = "app/ml/artifacts/test_model.joblib"

from app.db.session import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_client(client):
    client.post("/register", json={"email": "officer@example.com", "full_name": "Loan Officer", "password": "password123", "role": "admin"})
    client.post("/login", data={"email": "officer@example.com", "password": "password123"})
    return client


@pytest.fixture
def sample_payload():
    return {
        "applicant_name": "Ava Patel",
        "age": 35,
        "gender": "Female",
        "marital_status": "Married",
        "education": "Master",
        "employment_type": "Salaried",
        "years_employed": 7,
        "annual_income": 98000,
        "monthly_income": 8166.67,
        "existing_loans": 1,
        "loan_amount": 15000,
        "debt_to_income_ratio": 0.24,
        "dependents": 1,
        "credit_history_length": 8,
        "previous_defaults": 0,
        "credit_utilization": 0.28,
    }
