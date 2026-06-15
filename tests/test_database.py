from app.core.security import hash_password
from app.models import Application, User


def test_user_and_application_persist(db, sample_payload):
    user = User(email="db@example.com", full_name="DB User", password_hash=hash_password("password123"), role="loan_officer")
    db.add(user)
    db.commit()
    db.refresh(user)
    application = Application(**sample_payload, created_by_id=user.id)
    db.add(application)
    db.commit()
    db.refresh(application)
    assert application.id is not None
    assert db.query(Application).count() == 1
