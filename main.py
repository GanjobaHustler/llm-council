"""Entry point for Railway deployment — re-exports the FastAPI app."""

from backend.main import app  # noqa: F401  (uvicorn needs `main:app`)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
