from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db import Base, engine
from app import models  # noqa: F401
from app.api.routes import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # create_all is for local starter use only; use Alembic migrations for production.
    Base.metadata.create_all(bind=engine)
    if settings.demo_data_enabled:
        # Seed clearly labelled synthetic history for a zero-key local demo.
        from app.seed import seed
        seed()
    yield

app = FastAPI(
    title=settings.app_name,
    description="Smart Mandi pilot API. Public price browsing; sign-in required for bookings and buyer offers.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(router)

@app.get("/")
def root():
    return {"name": settings.app_name, "docs": "/docs", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "environment": settings.environment}
