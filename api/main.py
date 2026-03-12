"""FastAPI application for PDF Compiler web API."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .database import init_db
from .routes.auth import router as auth_router
from .routes.batches import router as batches_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup."""
    await init_db()
    yield


app = FastAPI(
    title="PDF Compiler API",
    description="Web API for processing PDFs and generating compiled learning guides",
    version="1.0.0",
    lifespan=lifespan,
)


class AllowAllCORSMiddleware(BaseHTTPMiddleware):
    """Allow any origin; reflect request Origin so credentials still work."""

    def _apply_cors(self, response: Response, origin: str | None) -> None:
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept"

    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        if request.method == "OPTIONS":
            response = Response(status_code=200)
            self._apply_cors(response, origin)
            return response
        response = await call_next(request)
        self._apply_cors(response, origin)
        return response


app.add_middleware(AllowAllCORSMiddleware)

app.include_router(auth_router)
app.include_router(batches_router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
