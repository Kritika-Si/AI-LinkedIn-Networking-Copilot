from fastapi import FastAPI

from database import Base, engine
import models


# Create database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AI LinkedIn Networking Copilot",
    description="An AI-powered assistant for professional networking.",
    version="1.0.0"
)


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