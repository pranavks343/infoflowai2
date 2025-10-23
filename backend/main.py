from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingestion, chat, admin, it_support  # make sure all files exist under routers/
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI(title="InfoFlow AI - Internal Knowledge Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add all API routers with correct prefixes
app.include_router(ingestion.router, prefix="/api/ingest", tags=["Ingestion"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(it_support.router, prefix="/api/it", tags=["IT Support"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
