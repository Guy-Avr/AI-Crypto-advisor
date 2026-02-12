from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, dashboard, onboarding, users, vote
from app.core.config import settings
from app.db.session import Base, engine
from app.models import Preferences, User, Vote

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(onboarding.router, prefix="/onboarding", tags=["onboarding"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(vote.router, prefix="/vote", tags=["vote"])