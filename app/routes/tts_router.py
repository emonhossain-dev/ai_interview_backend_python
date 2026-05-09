from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel, Field
from app.services.tts_service import generate_tts, DEFAULT_ELEVENLABS_VOICE

router = APIRouter(prefix="/tts", tags=["TTS"])


class TTSRequest(BaseModel):
    text    : str         = Field(..., min_length=1, max_length=1000)
    voice_id: str         = Field(default=DEFAULT_ELEVENLABS_VOICE)


@router.post(
    "",
    summary="Text-to-Speech",
    description="ElevenLabs TTS (Groq fallback). Returns raw audio bytes.",
    responses={
        200: {"content": {"audio/mpeg": {}, "audio/wav": {}}},
        503: {"description": "TTS service unavailable"},
    },
)
async def text_to_speech(req: TTSRequest):
    audio_bytes, mime_type = await generate_tts(req.text, req.voice_id)
    return Response(content=audio_bytes, media_type=mime_type)