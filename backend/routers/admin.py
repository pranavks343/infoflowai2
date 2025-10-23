# backend/routers/admin.py
from fastapi import APIRouter
import os
from rag.vector_store import vector_store_exists, VECTOR_DB_PATH

router = APIRouter()

@router.get("/stats")
def get_stats():
    files = os.listdir("data/uploaded_docs") if os.path.exists("data/uploaded_docs") else []
    return {
        "uploaded_docs_count": len(files),
        "files": files
    }

@router.get("/vector-store-status")
def get_vector_store_status():
    """Get the status of the vector store."""
    exists = vector_store_exists()
    return {
        "vector_store_exists": exists,
        "vector_store_path": VECTOR_DB_PATH,
        "status": "ready" if exists else "not_initialized",
        "message": "Vector store is ready for queries" if exists else "No documents have been ingested yet. Upload documents to initialize the vector store."
    }
