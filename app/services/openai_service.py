import os
from openai import OpenAI
from app.core.config import settings
import aiofiles
from pathlib import Path
import uuid
from typing import List, Dict

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # Directory for media storage
        self.media_dir = Path("media")
        self.media_dir.mkdir(exist_ok=True)

    def get_chat_response(self, system_message: str, messages: List[Dict]):
        # OpenAI Chat Completion
        formatted_messages = [{"role": "system", "content": system_message}]
        formatted_messages.extend(messages)
        
        response = self.client.chat.completions.create(
            model="gpt-4o", # latest
            messages=formatted_messages
        )
        return response.choices[0].message.content

    def generate_speech(self, text: str, voice: str = "alloy") -> str:
        # OpenAI TTS
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        # Save to file
        file_path = self.media_dir / f"{uuid.uuid4()}.mp3"
        response.stream_to_file(str(file_path))
        return str(file_path)

    def transcribe_audio(self, audio_file_path: str) -> str:
        # OpenAI Whisper
        with open(audio_file_path, "rb") as audio_file:
            transcript = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcript.text

openai_service = OpenAIService()
