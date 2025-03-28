from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.config import settings
from app.api.routes import router as api_router

# Create FastAPI app
app = FastAPI(
    title="University Regulations RAG Chatbot API",
    description="API for RAG-based chatbot for university regulations",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(
    api_router,
    prefix=f"{settings.API_PREFIX}{settings.API_V1_STR}",
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "University Regulations RAG Chatbot API",
        "docs_url": "/docs",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Create required directories
@app.on_event("startup")
async def startup_event():
    os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
    os.makedirs(settings.PROCESSED_DATA_DIR, exist_ok=True)
    os.makedirs(settings.VECTOR_STORE_DIR, exist_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8501, reload=True)