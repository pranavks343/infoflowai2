from fastapi import APIRouter
from pydantic import BaseModel
from rag.qa_pipeline import get_rag_chain

router = APIRouter()

class Query(BaseModel):
    query: str

@router.post("/query")
def it_query(query: Query):
    try:
        chain = get_rag_chain()
        result = chain({"query": query.query})

        sources = list({doc.metadata.get("source", "N/A") for doc in result.get("source_documents", [])})
        return {
            "answer": result["result"],
            "sources": sources
        }
    except Exception as e:
        if "Vector store not found" in str(e):
            return {
                "error": "⚠️ No documents have been indexed yet. Please upload documents first using the HR Dashboard.",
                "answer": None,
                "sources": []
            }
        else:
            return {
                "error": f"❌ An error occurred: {str(e)}",
                "answer": None,
                "sources": []
            }
