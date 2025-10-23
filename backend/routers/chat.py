# backend/routers/chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from rag.qa_pipeline import get_rag_chain

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def chat_query(req: QueryRequest):
    try:
        chain = get_rag_chain()
        result = chain({"query": req.query})

        sources = list({doc.metadata.get("source", "N/A") for doc in result.get("source_documents", [])})

        return {
            "answer": result["result"],
            "sources": sources
        }
    except Exception as e:
        if "Vector store not found" in str(e):
            return {
                "error": "No documents have been ingested yet. Please upload documents first using the /api/ingest/upload endpoint.",
                "answer": None,
                "sources": []
            }
        else:
            return {
                "error": f"An error occurred: {str(e)}",
                "answer": None,
                "sources": []
            }
