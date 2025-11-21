# app/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.db.database import init_db
from app.routes import upload, report


# -----------------------
# Middleware for API Token
# -----------------------
async def verify_token(request: Request, call_next):
    protected_paths = ["/generate-report"]

    if any(request.url.path.startswith(p) for p in protected_paths):
        provided = request.headers.get("Authorization")

        if not provided:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing Authorization header"},
            )

        # EXACT MATCH — Your token is 12345
        if provided.strip() != settings.API_TOKEN:
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid API token"},
            )

    return await call_next(request)


# -----------------------
# Swagger Auth Button
# -----------------------
def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title="DataLens API",
        version="1.0.0",
        description="Automated dataset ingestion + vector storage + Groq-powered reporting.",
        routes=app.routes,
    )

    # Add security scheme
    schema["components"]["securitySchemes"] = {
        "ApiTokenAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
        }
    }

    # Secure ONLY this endpoint
    if "/generate-report" in schema["paths"]:
        for method in schema["paths"]["/generate-report"]:
            schema["paths"]["/generate-report"][method]["security"] = [
                {"ApiTokenAuth": []}
            ]

    app.openapi_schema = schema
    return schema


# -----------------------
# App Factory
# -----------------------
def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add API token middleware
    app.add_middleware(BaseHTTPMiddleware, dispatch=verify_token)

    @app.on_event("startup")
    def start_db():
        init_db()

    # Routes
    app.include_router(upload.router)
    app.include_router(report.router)

    # Override swagger schema
    app.openapi = lambda: custom_openapi(app)

    return app


app = create_app()
