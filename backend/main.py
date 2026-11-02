from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI

from database import Base, engine
import models

from routers.profiles import router as profiles_router


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI LinkedIn Networking Copilot",
    description="An AI-powered assistant for professional networking.",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Profile API routes
app.include_router(profiles_router)


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