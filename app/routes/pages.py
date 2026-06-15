from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Application, Prediction, Report, User
from app.schemas import ApplicationInput, UserCreate
from app.services.auth import authenticate_user, create_user, current_user, log_action
from app.services.dashboard import dashboard_summary
from app.services.prediction import predict_application
from app.services.reports import generate_pdf_report

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


def context(request: Request, db: Session, extra: dict | None = None):
    user = db.get(User, request.session["user_id"]) if request.session.get("user_id") else None
    data = {"request": request, "user": user, "app_name": "CreditWise AI"}
    data.update(extra or {})
    return data


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard-view", status_code=303)
    return templates.TemplateResponse(request, "login.html", context(request, db))


@router.get("/register-view", response_class=HTMLResponse)
def register_view(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, "register.html", context(request, db))


@router.post("/register-view")
def register_submit(request: Request, full_name: str = Form(...), email: str = Form(...), password: str = Form(...), role: str = Form("loan_officer"), db: Session = Depends(get_db)):
    if role == "admin" and db.query(User).filter(User.role == "admin").count() > 0:
        role = "loan_officer"
    user = create_user(db, UserCreate(full_name=full_name, email=email, password=password, role=role))
    request.session["user_id"] = user.id
    return RedirectResponse("/dashboard-view", status_code=303)


@router.post("/login-view")
def login_submit(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(request, "login.html", context(request, db, {"error": "Invalid email or password"}), status_code=401)
    request.session["user_id"] = user.id
    log_action(db, user.id, "login", "users", user.id)
    return RedirectResponse("/dashboard-view", status_code=303)


@router.get("/logout-view")
def logout_view(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=303)


@router.get("/dashboard-view", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(get_db), user=Depends(current_user)):
    return templates.TemplateResponse(request, "dashboard.html", context(request, db, {"summary": dashboard_summary(db)}))


@router.get("/predict-view", response_class=HTMLResponse)
def predict_view(request: Request, db: Session = Depends(get_db), user=Depends(current_user)):
    return templates.TemplateResponse(request, "predict.html", context(request, db))


@router.post("/predict-view", response_class=HTMLResponse)
def predict_submit(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(current_user),
    applicant_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    marital_status: str = Form(...),
    education: str = Form(...),
    employment_type: str = Form(...),
    years_employed: float = Form(...),
    annual_income: float = Form(...),
    monthly_income: float = Form(...),
    existing_loans: int = Form(...),
    loan_amount: float = Form(...),
    debt_to_income_ratio: float = Form(...),
    dependents: int = Form(...),
    credit_history_length: float = Form(...),
    previous_defaults: int = Form(...),
    credit_utilization: float = Form(...),
):
    payload = ApplicationInput(
        applicant_name=applicant_name,
        age=age,
        gender=gender,
        marital_status=marital_status,
        education=education,
        employment_type=employment_type,
        years_employed=years_employed,
        annual_income=annual_income,
        monthly_income=monthly_income,
        existing_loans=existing_loans,
        loan_amount=loan_amount,
        debt_to_income_ratio=debt_to_income_ratio,
        dependents=dependents,
        credit_history_length=credit_history_length,
        previous_defaults=previous_defaults,
        credit_utilization=credit_utilization,
    )
    application = Application(**payload.model_dump(), created_by_id=user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    db.add(Prediction(application_id=application.id, **predict_application(payload.model_dump())))
    db.commit()
    db.refresh(application)
    return templates.TemplateResponse(request, "result.html", context(request, db, {"application": application}))


@router.get("/applications-view", response_class=HTMLResponse)
def applications_view(request: Request, search: str = "", decision: str = "", risk: str = "", db: Session = Depends(get_db), user=Depends(current_user)):
    query = db.query(Application).options(joinedload(Application.prediction))
    if search:
        query = query.filter(Application.applicant_name.ilike(f"%{search}%"))
    if decision:
        query = query.join(Prediction).filter(Prediction.decision == decision)
    if risk:
        query = query.join(Prediction).filter(Prediction.risk_level == risk)
    applications = query.order_by(Application.created_at.desc()).all()
    return templates.TemplateResponse(request, "applications.html", context(request, db, {"applications": applications, "filters": {"search": search, "decision": decision, "risk": risk}}))


@router.get("/reports/{application_id}/download")
def download_report(application_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    application = db.query(Application).options(joinedload(Application.prediction)).filter(Application.id == application_id).first()
    if not application or not application.prediction:
        raise HTTPException(status_code=404, detail="Application not found")
    report = db.query(Report).filter(Report.application_id == application.id).order_by(Report.created_at.desc()).first()
    path = report.file_path if report and Path(report.file_path).exists() else generate_pdf_report(application)
    if not report:
        db.add(Report(application_id=application.id, file_path=path))
        db.commit()
    return FileResponse(path, media_type="application/pdf", filename=f"creditwise_report_{application.id}.pdf")
