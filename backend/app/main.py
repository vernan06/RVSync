"""RVSync - Learning Management & Career Development Platform

FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.config import get_settings
from app.database import init_db
from app.routers import auth, users, classrooms, courses, assignments, tests, chat, announcements, career, admin, events, ai_support


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Initialize database
    print("🚀 Starting RVSync...")
    init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("👋 Shutting down RVSync...")


# Create FastAPI app
app = FastAPI(
    title="RVSync API",
    description="Autonomous Learning Management & Career Development Platform",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(classrooms.router)
app.include_router(courses.router)
app.include_router(assignments.router)
app.include_router(tests.router)
app.include_router(chat.router)
app.include_router(announcements.router)
app.include_router(career.router)
app.include_router(admin.router)
app.include_router(events.router)
app.include_router(ai_support.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "name": "RVSync API",
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """API health check"""
    return {"status": "healthy"}


# Run with: uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
