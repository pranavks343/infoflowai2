# backend/rag/vector_store.py

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings  # ✅ Use updated import
from langchain_core.documents import Document
import os

VECTOR_DB_PATH = "faiss_index"

def get_embedding():
    """Returns an instance of the OpenAI Embeddings class."""
    return OpenAIEmbeddings()

def store_embeddings(docs: list[Document]):
    """
    Creates or updates a FAISS vector store by embedding the provided documents.
    If a FAISS index already exists, it adds the new documents.
    """
    embedding = get_embedding()
    if os.path.exists(VECTOR_DB_PATH):
        db = FAISS.load_local(VECTOR_DB_PATH, embedding, allow_dangerous_deserialization=True)
        db.add_documents(docs)
    else:
        db = FAISS.from_documents(docs, embedding)
    db.save_local(VECTOR_DB_PATH)

def get_vector_db():
    """
    Loads the FAISS vector store from local disk.
    Raises an exception if the index does not exist.
    """
    if not vector_store_exists():
        raise Exception("Vector store not found")
    return FAISS.load_local(
        VECTOR_DB_PATH,
        get_embedding(),
        allow_dangerous_deserialization=True  # ✅ Required for safe local load
    )

def vector_store_exists():
    """Returns True if the FAISS vector store directory exists."""
    return os.path.exists(VECTOR_DB_PATH)
