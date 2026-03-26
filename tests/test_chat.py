import pytest
from unittest.mock import patch, AsyncMock

def test_manage_sessions(client):
    # 1. Create Agent
    res = client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    agent_id = res.json()["id"]
    
    # 2. Start session
    session_res = client.post(f"/agents/{agent_id}/sessions")
    assert session_res.status_code == 200
    session_id = session_res.json()["id"]
    
    # 3. List sessions
    list_res = client.get(f"/agents/{agent_id}/sessions")
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

@patch("app.services.openai_service.openai_service.get_chat_response", new_callable=AsyncMock)
def test_chat_text_with_session(mock_chat, client):
    # Setup
    res = client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    agent_id = res.json()["id"]
    session_res = client.post(f"/agents/{agent_id}/sessions")
    session_id = session_res.json()["id"]
    
    mock_chat.return_value = "Hello from AI"
    
    # Act
    chat_res = client.post(
        f"/agents/{agent_id}/sessions/{session_id}/chat",
        data={"message": "Hi agent"}
    )
    
    # Assert
    assert chat_res.status_code == 200
    assert chat_res.json()["response"] == "Hello from AI"

@patch("app.services.openai_service.openai_service.transcribe_audio", new_callable=AsyncMock)
@patch("app.services.openai_service.openai_service.get_chat_response", new_callable=AsyncMock)
@patch("app.services.openai_service.openai_service.generate_speech", new_callable=AsyncMock)
def test_voice_chat_with_session(mock_speech, mock_chat, mock_transcribe, client):
    # Setup
    res = client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    agent_id = res.json()["id"]
    session_res = client.post(f"/agents/{agent_id}/sessions")
    session_id = session_res.json()["id"]
    
    mock_transcribe.return_value = "Hello assistant"
    mock_chat.return_value = "Hello user"
    mock_speech.return_value = "media/test.mp3"
    
    files = {"audio": ("test.wav", b"fake audio content", "audio/wav")}
    
    # Act
    chat_res = client.post(
        f"/agents/{agent_id}/sessions/{session_id}/voice-chat",
        files=files,
        data={"generate_audio": "true"}
    )
    
    # Assert
    assert chat_res.status_code == 200
    assert chat_res.json()["response"] == "Hello user"
    assert "audio_url" in chat_res.json()
