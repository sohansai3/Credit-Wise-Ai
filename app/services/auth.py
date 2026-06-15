from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.db.session import get_db
from app.models import AuditLog, User
from app.schemas import UserCreate


def create_user(db: Session, payload: UserCreate) -> User:
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email is already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, user.id, "register", "users", user.id, {"role": user.role})
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email.lower(), User.is_active.is_(True)).first()
    if user and verify_password(password, user.password_hash):
        return user
    return None


def log_action(db: Session, user_id: int | None, action: str, entity: str, entity_id: int | None = None, details: dict | None = None) -> None:
    db.add(AuditLog(user_id=user_id, action=action, entity=entity, entity_id=entity_id, details=details or {}))
    db.commit()


def current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user


def admin_user(user: User = Depends(current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
