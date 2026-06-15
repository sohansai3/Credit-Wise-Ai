from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="loan_officer", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    applications: Mapped[list["Application"]] = relationship(back_populates="created_by")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    applicant_name: Mapped[str] = mapped_column(String(255), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=False)
    marital_status: Mapped[str] = mapped_column(String(50), nullable=False)
    education: Mapped[str] = mapped_column(String(100), nullable=False)
    employment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    years_employed: Mapped[float] = mapped_column(Float, nullable=False)
    annual_income: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)
    existing_loans: Mapped[int] = mapped_column(Integer, nullable=False)
    loan_amount: Mapped[float] = mapped_column(Float, nullable=False)
    debt_to_income_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    dependents: Mapped[int] = mapped_column(Integer, nullable=False)
    credit_history_length: Mapped[float] = mapped_column(Float, nullable=False)
    previous_defaults: Mapped[int] = mapped_column(Integer, nullable=False)
    credit_utilization: Mapped[float] = mapped_column(Float, nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    created_by: Mapped[User | None] = relationship(back_populates="applications")
    prediction: Mapped["Prediction"] = relationship(back_populates="application", cascade="all, delete-orphan", uselist=False)
    reports: Mapped[list["Report"]] = relationship(back_populates="application", cascade="all, delete-orphan")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), unique=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    approval_probability: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    credit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    recommended_credit_limit: Mapped[float] = mapped_column(Float, nullable=False)
    financial_stability_score: Mapped[float] = mapped_column(Float, nullable=False)
    repayment_capacity_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    final_applicant_score: Mapped[float] = mapped_column(Float, nullable=False)
    top_approval_factors: Mapped[list] = mapped_column(JSON, nullable=False)
    top_rejection_factors: Mapped[list] = mapped_column(JSON, nullable=False)
    feature_importance: Mapped[list] = mapped_column(JSON, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    application: Mapped[Application] = relationship(back_populates="prediction")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id"), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    application: Mapped[Application] = relationship(back_populates="reports")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
