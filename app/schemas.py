from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    role: str = "loan_officer"

    @field_validator("role")
    @classmethod
    def role_allowed(cls, value: str) -> str:
        if value not in {"admin", "loan_officer"}:
            raise ValueError("role must be admin or loan_officer")
        return value


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class ApplicationInput(BaseModel):
    applicant_name: str = Field(min_length=2, max_length=255)
    age: int = Field(ge=18, le=100)
    gender: str
    marital_status: str
    education: str
    employment_type: str
    years_employed: float = Field(ge=0, le=60)
    annual_income: float = Field(gt=0)
    monthly_income: float = Field(gt=0)
    existing_loans: int = Field(ge=0, le=50)
    loan_amount: float = Field(ge=0)
    debt_to_income_ratio: float = Field(ge=0, le=1.5)
    dependents: int = Field(ge=0, le=20)
    credit_history_length: float = Field(ge=0, le=80)
    previous_defaults: int = Field(ge=0, le=20)
    credit_utilization: float = Field(ge=0, le=1.5)


class PredictionRead(BaseModel):
    decision: str
    approval_probability: float
    confidence_score: float
    credit_score: int
    risk_level: str
    recommended_credit_limit: float
    financial_stability_score: float
    repayment_capacity_score: float
    risk_score: float
    final_applicant_score: float
    top_approval_factors: list[dict]
    top_rejection_factors: list[dict]
    feature_importance: list[dict]
    explanation: str
    model_name: str
    metrics: dict

    model_config = {"from_attributes": True}


class ApplicationRead(ApplicationInput):
    id: int
    created_at: datetime
    prediction: PredictionRead | None = None
    model_config = {"from_attributes": True}
