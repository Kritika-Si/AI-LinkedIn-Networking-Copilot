
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
import models

from routers.profiles import router as profiles_router
from routers.recommendations import router as recommendations_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI LinkedIn Networking Copilot",
    description="An AI-powered assistant for professional networking.",
    version="1.0.0"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "DELETE"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
)


# Register API routes
app.include_router(profiles_router)
app.include_router(recommendations_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to AI LinkedIn Networking Copilot!",
        "status": "Backend is running successfully"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI LinkedIn Networking Copilot"
    }
