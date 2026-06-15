from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import User
from app.services.auth import admin_user

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="app/templates")


@router.get("/admin/users", response_class=HTMLResponse)
def users(request: Request, db: Session = Depends(get_db), admin=Depends(admin_user)):
    return templates.TemplateResponse(request, "admin_users.html", {"request": request, "user": admin, "users": db.query(User).order_by(User.created_at.desc()).all(), "app_name": "CreditWise AI"})


@router.post("/admin/users/{user_id}/toggle")
def toggle_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_user)):
    user = db.get(User, user_id)
    if user and user.id != admin.id:
        user.is_active = not user.is_active
        db.commit()
    return RedirectResponse("/admin/users", status_code=303)
