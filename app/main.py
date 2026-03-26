import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.api import agents, chat
from app.core.database import engine, Base
from app.core.config import settings
import os

# Initialize database
# In a real app we would use Alembic for migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

# Media directory for audio files
os.makedirs("media", exist_ok=True)
app.mount("/static", StaticFiles(directory="media"), name="static")

# Routes
app.include_router(agents.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Welcome to AI Agent Platform API"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
