"""FastAPI application for PDF Compiler web API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.batches import router as batches_router

app = FastAPI(
    title="PDF Compiler API",
    description="Web API for processing PDFs and generating compiled learning guides",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://127.0.0.1:5173", "http://127.0.0.1:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(batches_router)


@app.get("/api/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
