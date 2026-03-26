import pytest
from unittest.mock import patch, AsyncMock

@patch("app.services.openai_service.openai_service.get_chat_response", new_callable=AsyncMock)
def test_chat_text(mock_chat, client):
    # Pre-create agent
    res = client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    agent_id = res.json()["id"]
    
    mock_chat.return_value = "Hello from AI"
    
    chat_res = client.post(
        f"/agents/{agent_id}/chat",
        data={"message": "Hi agent"}
    )
    
    assert chat_res.status_code == 200
    assert chat_res.json()["response"] == "Hello from AI"

@patch("app.services.openai_service.openai_service.transcribe_audio", new_callable=AsyncMock)
@patch("app.services.openai_service.openai_service.get_chat_response", new_callable=AsyncMock)
@patch("app.services.openai_service.openai_service.generate_speech", new_callable=AsyncMock)
def test_voice_chat(mock_speech, mock_chat, mock_transcribe, client):
    # Pre-create agent
    res = client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    agent_id = res.json()["id"]
    
    mock_transcribe.return_value = "Hello assistant"
    mock_chat.return_value = "Hello user"
    mock_speech.return_value = "media/test.mp3"
    
    # Mock audio file
    files = {"audio": ("test.wav", b"fake audio content", "audio/wav")}
    
    chat_res = client.post(
        f"/agents/{agent_id}/voice-chat",
        files=files,
        data={"generate_audio": "true"}
    )
    
    assert chat_res.status_code == 200
    assert chat_res.json()["response"] == "Hello user"
    assert "audio_url" in chat_res.json()
