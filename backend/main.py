from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
import uvicorn

load_dotenv(Path(__file__).resolve().parent / ".env")

from routers import ingestion, chat, admin, it_support

app = FastAPI(title="InfoFlow AI - Internal Knowledge Assistant")

# Add all API routers with correct prefixes
app.include_router(ingestion.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(it_support.router, prefix="/api/it", tags=["IT Support"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
