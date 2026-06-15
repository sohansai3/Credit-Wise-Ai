import csv
import io

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models import Application, Prediction, Report, User
from app.schemas import ApplicationInput, ApplicationRead, UserCreate, UserRead
from app.services.auth import admin_user, authenticate_user, create_user, current_user, log_action
from app.services.dashboard import dashboard_summary
from app.services.prediction import predict_application
from app.services.reports import generate_pdf_report

router = APIRouter(tags=["api"])


@router.post("/register", response_model=UserRead)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role == "admin" and db.query(User).filter(User.role == "admin").count() > 0:
        payload.role = "loan_officer"
    return create_user(db, payload)


@router.post("/login")
def login(request: Request, email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user_id"] = user.id
    log_action(db, user.id, "login", "users", user.id)
    return {"message": "Logged in", "user": UserRead.model_validate(user)}


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out"}


@router.post("/predict", response_model=ApplicationRead)
def predict(payload: ApplicationInput, db: Session = Depends(get_db), user=Depends(current_user)):
    application = Application(**payload.model_dump(), created_by_id=user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    result = predict_application(payload.model_dump())
    db.add(Prediction(application_id=application.id, **result))
    db.commit()
    db.refresh(application)
    log_action(db, user.id, "predict", "applications", application.id, {"decision": application.prediction.decision})
    return application


@router.get("/applications", response_model=list[ApplicationRead])
def applications(search: str = "", decision: str = "", risk: str = "", sort: str = "created_at", db: Session = Depends(get_db), user=Depends(current_user)):
    query = db.query(Application).options(joinedload(Application.prediction))
    if search:
        query = query.filter(Application.applicant_name.ilike(f"%{search}%"))
    if decision:
        query = query.join(Prediction).filter(Prediction.decision == decision)
    if risk:
        query = query.join(Prediction).filter(Prediction.risk_level == risk)
    sort_map = {"created_at": Application.created_at.desc(), "name": Application.applicant_name.asc(), "income": Application.annual_income.desc(), "score": Prediction.credit_score.desc()}
    if sort == "score":
        query = query.join(Prediction)
    return query.order_by(sort_map.get(sort, Application.created_at.desc())).all()


@router.get("/applications/export")
def export_applications(db: Session = Depends(get_db), user=Depends(current_user)):
    rows = db.query(Application).options(joinedload(Application.prediction)).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "applicant_name", "decision", "credit_score", "risk_level", "approval_probability", "recommended_credit_limit"])
    for application in rows:
        prediction = application.prediction
        writer.writerow(
            [
                application.id,
                application.applicant_name,
                prediction.decision if prediction else "",
                prediction.credit_score if prediction else "",
                prediction.risk_level if prediction else "",
                prediction.approval_probability if prediction else "",
                prediction.recommended_credit_limit if prediction else "",
            ]
        )
    return Response(buf.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=creditwise_applications.csv"})


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), user=Depends(current_user)):
    return dashboard_summary(db)


@router.get("/reports")
def reports(db: Session = Depends(get_db), user=Depends(current_user)):
    return db.query(Report).all()


@router.post("/reports/{application_id}")
def create_report(application_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    application = db.query(Application).options(joinedload(Application.prediction)).filter(Application.id == application_id).first()
    if not application or not application.prediction:
        raise HTTPException(status_code=404, detail="Application or prediction not found")
    path = generate_pdf_report(application)
    report = Report(application_id=application.id, file_path=path)
    db.add(report)
    db.commit()
    log_action(db, user.id, "generate_report", "applications", application.id, {"path": path})
    return {"report_id": report.id, "file_path": path}


@router.delete("/application/{application_id}")
def delete_application(application_id: int, db: Session = Depends(get_db), user=Depends(admin_user)):
    application = db.get(Application, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(application)
    db.commit()
    log_action(db, user.id, "delete", "applications", application_id)
    return {"message": "Application deleted"}
