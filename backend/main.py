from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from pathlib import Path
import uvicorn

load_dotenv(Path(__file__).resolve().parent / ".env")

from routers import ingestion, chat, admin, it_support
from auth import current_user, require_roles

app = FastAPI(title="InfoFlow AI - Internal Knowledge Assistant")

# Add all API routers with correct prefixes
app.include_router(ingestion.router, prefix="/api/ingest", tags=["Ingestion"], dependencies=[Depends(require_roles("HR", "Admin"))])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"], dependencies=[Depends(current_user)])
app.include_router(it_support.router, prefix="/api/it", tags=["IT Support"], dependencies=[Depends(require_roles("IT", "Admin"))])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"], dependencies=[Depends(require_roles("HR", "Admin"))])

@app.get("/api/auth/me")
def me(user=Depends(current_user)):
    return user


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
