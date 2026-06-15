from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
from app.routes import admin, api, pages

settings = get_settings()
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site="lax", https_only=False)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api.router)
app.include_router(pages.router)
app.include_router(admin.router)
