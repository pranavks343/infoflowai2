from fastapi import APIRouter, UploadFile, File
from rag.document_loader import load_and_split_document
from rag.vector_store import store_embeddings
import os

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        print(f"🚀 Received file: {file.filename}")

        # Process and split document
        chunks = await load_and_split_document(file)
        print(f"✅ Loaded and split into {len(chunks)} chunks")

        # Store in vector DB
        store_embeddings(chunks)
        print("✅ Embeddings stored in FAISS")

        return {"message": "File processed and embedded successfully"}
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return {"error": str(e)}

@router.get("/test-init")
def init_dummy_vector_db():
    from langchain_core.documents import Document
    from rag.vector_store import store_embeddings

    docs = [Document(page_content="Hello, this is a test document.")]
    store_embeddings(docs)
    return {"status": "Test FAISS DB initialized"}
