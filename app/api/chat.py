from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.agent import Agent, Message, Conversation
from app.schemas.agent import ChatResponse
from app.services.openai_service import openai_service
from pathlib import Path
import uuid
import shutil

router = APIRouter(prefix="/agents", tags=["Chat"])

@router.post("/{agent_id}/chat", response_model=ChatResponse)
def chat_with_agent(
    agent_id: int, 
    message: str = Form(...), 
    generate_audio: bool = Form(False),
    db: Session = Depends(get_db)
):
    # 1. Fetch Agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # 2. Get AI Response
    # In a real app we would maintain conversation state, for assessment let's keep it simple
    try:
        response_text = openai_service.get_chat_response(
            agent.system_prompt, 
            [{"role": "user", "content": message}]
        )
        
        audio_url = None
        if generate_audio:
            audio_path = openai_service.generate_speech(response_text, agent.voice_id)
            audio_url = f"/static/{Path(audio_path).name}"
            
        return ChatResponse(response=response_text, audio_url=audio_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

@router.post("/{agent_id}/voice-chat", response_model=ChatResponse)
async def voice_chat_with_agent(
    agent_id: int, 
    audio: UploadFile = File(...), 
    generate_audio: bool = Form(True),
    db: Session = Depends(get_db)
):
    # 1. Fetch Agent
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # 2. Save uploaded audio temporarily
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4()}_{audio.filename}"
    
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(audio.file, buffer)
        
    try:
        # 3. Transcribe STT
        transcribed_text = openai_service.transcribe_audio(str(temp_path))
        
        # 4. Get Agent Response
        response_text = openai_service.get_chat_response(
            agent.system_prompt, 
            [{"role": "user", "content": transcribed_text}]
        )
        
        # 5. Generate TTS
        audio_url = None
        if generate_audio:
            audio_path = openai_service.generate_speech(response_text, agent.voice_id)
            audio_url = f"/static/{Path(audio_path).name}"
            
        return ChatResponse(response=response_text, audio_url=audio_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
