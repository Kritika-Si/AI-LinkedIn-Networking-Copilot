
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers.auth import router as auth_router
from routers.profiles import router as profiles_router
from routers.recommendations import router as recommendations_router


ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app = FastAPI(
    title="AI LinkedIn Networking Copilot",
    description="An AI-powered assistant for professional networking.",
    version="1.0.0"
)


# Validate browser origins for state-changing requests.
@app.middleware("http")
async def validate_request_origin(request: Request, call_next):
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")

        # Reject requests from untrusted browser origins.
        if origin and origin not in ALLOWED_ORIGINS:
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "Request origin is not allowed."
                },
            )

    return await call_next(request)


# Configure CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE"
    ],
    allow_headers=[
        "Content-Type",
        "Authorization"
    ],
)


# Register API routes.
app.include_router(auth_router)
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
