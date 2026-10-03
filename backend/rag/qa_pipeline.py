# backend/rag/qa_pipeline.py
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from .vector_store import get_vector_db
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

def get_rag_chain():
    db = get_vector_db()
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain
