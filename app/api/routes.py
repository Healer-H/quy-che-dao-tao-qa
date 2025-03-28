from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import shutil

from app.config import settings
from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import EmbeddingsManager
from app.rag.retriever import DocumentRetriever
from app.rag.rag_pipeline import RAGPipeline

# Initialize router
router = APIRouter()

# Initialize RAG components
embeddings_manager = EmbeddingsManager(
    embedding_model_name=settings.EMBEDDING_MODEL_NAME,
    vector_store_path=settings.VECTOR_STORE_DIR
)

document_processor = DocumentProcessor(
    chunk_size=settings.CHUNK_SIZE,
    chunk_overlap=settings.CHUNK_OVERLAP,
    raw_dir=settings.RAW_DATA_DIR,
    processed_dir=settings.PROCESSED_DATA_DIR
)

retriever = DocumentRetriever(embeddings_manager)

rag_pipeline = RAGPipeline(
    retriever=retriever,
    model_name=settings.MODEL_NAME,
    temperature=settings.TEMPERATURE,
    max_tokens=settings.MAX_TOKENS
)

# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    source_filter: Optional[str] = None

class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    sources: List[Dict[str, Any]]

class DocumentResponse(BaseModel):
    """Document response model"""
    document_id: str
    filename: str
    chunk_count: int
    status: str

# Routes
@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Generate response with RAG pipeline"""
    try:
        result = rag_pipeline.generate_response(
            query=request.message,
            k=settings.RETRIEVER_K,
            source_filter=request.source_filter
        )
        print(f"Chat response: {result}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_id: Optional[str] = Form(None)
):
    """Upload document and process it in the background"""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save file to raw directory
    file_path = os.path.join(settings.RAW_DATA_DIR, file.filename)
    
    try:
        # Create directory if it doesn't exist
        os.makedirs(settings.RAW_DATA_DIR, exist_ok=True)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document in background
        background_tasks.add_task(process_document, file.filename)
        
        # Add status tracking
        print(f"Started background processing of {file.filename}")
        
        return {
            "document_id": document_id or os.path.splitext(file.filename)[0],
            "filename": file.filename,
            "chunk_count": 0,  # Will be updated after processing
            "status": "processing"
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents():
    """List all processed documents"""
    try:
        documents = []
        # List files in raw directory
        if os.path.exists(settings.RAW_DATA_DIR):
            for filename in os.listdir(settings.RAW_DATA_DIR):
                if filename.lower().endswith(".pdf"):
                    doc_id = os.path.splitext(filename)[0]
                    documents.append({
                        "document_id": doc_id,
                        "filename": filename,
                        "status": "processed" if is_document_processed(doc_id) else "pending"
                    })
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def is_document_processed(doc_id: str) -> bool:
    """Check if document has been processed"""
    chunks_path = os.path.join(settings.PROCESSED_DATA_DIR, f"{doc_id}_chunks.json")
    return os.path.exists(chunks_path)

async def process_document(filename: str):
    """Process document and add to vector store"""
    try:
        # Process PDF
        chunks = document_processor.process_pdf(filename)
        if not chunks:
            return
        
        # Save chunks
        document_processor.save_chunks({filename: chunks})
        
        # Add to vector store
        embeddings_manager.add_documents(chunks)
    except Exception as e:
        print(f"Error processing document {filename}: {str(e)}")