from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.agent import Agent, Message, Conversation
from app.schemas.agent import ChatResponse, SessionResponse
from app.services.openai_service import openai_service
from pathlib import Path
import uuid
import aiofiles
from typing import List

router = APIRouter(prefix="/agents", tags=["Sessions & Chat"])

@router.post("/{agent_id}/sessions", response_model=SessionResponse)
def start_session(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    session = Conversation(agent_id=agent_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/{agent_id}/sessions", response_model=List[SessionResponse])
def list_sessions(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return db.query(Conversation).filter(Conversation.agent_id == agent_id).all()

@router.get("/{agent_id}/sessions/{session_id}", response_model=SessionResponse)
def get_session(agent_id: int, session_id: int, db: Session = Depends(get_db)):
    session = db.query(Conversation).filter(
        Conversation.id == session_id,
        Conversation.agent_id == agent_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/{agent_id}/sessions/{session_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: int,
    session_id: int,
    message: str = Form(...), 
    generate_audio: bool = Form(False),
    db: Session = Depends(get_db)
):
    # 1. Fetch Agent and Session
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    session = db.query(Conversation).filter(
        Conversation.id == session_id,
        Conversation.agent_id == agent_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found for this agent")
    
    # 2. Prepare context from history
    # Fetch last 10 messages for context (simple memory)
    history = db.query(Message).filter(Message.conversation_id == session_id).order_by(Message.created_at.asc()).all()
    messages_context = [{"role": m.role, "content": m.content} for m in history]

    # 3. Get AI Response
    try:
        response_text = await openai_service.get_chat_response(
            agent.system_prompt, 
            messages_context + [{"role": "user", "content": message}]
        )
        
        audio_path = None
        audio_url = None
        if generate_audio:
            audio_path = await openai_service.generate_speech(response_text, agent.voice_id)
            audio_url = f"/static/{Path(audio_path).name}"
        
        # 4. Save messages to DB
        user_msg = Message(conversation_id=session.id, role="user", content=message)
        assistant_msg = Message(
            conversation_id=session.id, 
            role="assistant", 
            content=response_text,
            audio_path=audio_path
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
            
        return ChatResponse(response=response_text, audio_url=audio_url)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")

@router.post("/{agent_id}/sessions/{session_id}/voice-chat", response_model=ChatResponse)
async def voice_chat_with_agent(
    agent_id: int,
    session_id: int,
    audio: UploadFile = File(...), 
    generate_audio: bool = Form(True),
    db: Session = Depends(get_db)
):
    # 1. Fetch Agent and Session
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    session = db.query(Conversation).filter(
        Conversation.id == session_id,
        Conversation.agent_id == agent_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found for this agent")

    # 2. Save uploaded audio temporarily
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    temp_path = temp_dir / f"{uuid.uuid4()}_{audio.filename}"
    
    async with aiofiles.open(temp_path, "wb") as buffer:
        content = await audio.read()
        await buffer.write(content)
        
    try:
        # 3. Transcribe STT
        transcribed_text = await openai_service.transcribe_audio(str(temp_path))
        
        # 4. Fetch context
        history = db.query(Message).filter(Message.conversation_id == session_id).order_by(Message.created_at.asc()).all()
        messages_context = [{"role": m.role, "content": m.content} for m in history]

        # 5. Get Agent Response
        response_text = await openai_service.get_chat_response(
            agent.system_prompt, 
            messages_context + [{"role": "user", "content": transcribed_text}]
        )
        
        # 6. Generate TTS
        audio_path = None
        audio_url = None
        if generate_audio:
            audio_path = await openai_service.generate_speech(response_text, agent.voice_id)
            audio_url = f"/static/{Path(audio_path).name}"
        
        # 7. Save messages to DB
        user_msg = Message(conversation_id=session.id, role="user", content=transcribed_text)
        assistant_msg = Message(
            conversation_id=session.id, 
            role="assistant", 
            content=response_text,
            audio_path=audio_path
        )
        db.add(user_msg)
        db.add(assistant_msg)
        db.commit()
            
        return ChatResponse(response=response_text, audio_url=audio_url)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"OpenAI Error: {str(e)}")
    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
