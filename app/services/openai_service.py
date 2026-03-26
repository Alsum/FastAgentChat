import os
from openai import AsyncOpenAI
from app.core.config import settings
import aiofiles
from pathlib import Path
import uuid
from typing import List, Dict

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        # Directory for media storage
        self.media_dir = Path("media")
        self.media_dir.mkdir(exist_ok=True)

    async def get_chat_response(self, system_message: str, messages: List[Dict]):
        # OpenAI Chat Completion
        formatted_messages = [{"role": "system", "content": system_message}]
        formatted_messages.extend(messages)
        
        response = await self.client.chat.completions.create(
            model="gpt-4o", # latest
            messages=formatted_messages
        )
        return response.choices[0].message.content

    async def generate_speech(self, text: str, voice: str = "alloy") -> str:
        # OpenAI TTS
        response = await self.client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        # Save to file
        file_path = self.media_dir / f"{uuid.uuid4()}.mp3"
        # stream_to_file is synchronous, but we can write content manually with aiofiles
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(response.content)
        return str(file_path)

    async def transcribe_audio(self, audio_file_path: str) -> str:
        # OpenAI Whisper
        async with aiofiles.open(audio_file_path, "rb") as audio_file:
            content = await audio_file.read()
            # The SDK expects file-like object or bytes
            transcript = await self.client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.mp3", content)
            )
        return transcript.text

openai_service = OpenAIService()
