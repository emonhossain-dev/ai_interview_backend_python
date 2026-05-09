import os
import httpx
from fastapi import HTTPException

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
GROQ_API_KEY       = os.getenv("GROQ_API_KEY")

ELEVENLABS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
GROQ_TTS_URL   = "https://api.groq.com/openai/v1/audio/speech"

# Default voice IDs — override per-request
DEFAULT_ELEVENLABS_VOICE = "EXAVITQu4vr4xnSDxMaL"  # Rachel
DEFAULT_GROQ_VOICE       = "Fritz-PlayAI"


async def generate_tts(text: str, voice_id: str = DEFAULT_ELEVENLABS_VOICE) -> tuple[bytes, str]:
    """
    TTS generate করো।
    Returns: (audio_bytes, mime_type)
    ElevenLabs → fail হলে Groq fallback
    """
    # ── Primary: ElevenLabs ──────────────────────────────────────────────────
    if ELEVENLABS_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.post(
                    ELEVENLABS_URL.format(voice_id=voice_id),
                    headers={
                        "xi-api-key"  : ELEVENLABS_API_KEY,
                        "Content-Type": "application/json",
                    },
                    json={
                        "text"          : text,
                        "model_id"      : "eleven_turbo_v2",
                        "voice_settings": {
                            "stability"       : 0.5,
                            "similarity_boost": 0.75,
                            "style"           : 0.3,
                            "use_speaker_boost": True,
                        },
                    },
                )
            if resp.status_code == 200:
                return resp.content, "audio/mpeg"
            else:
                print(f"⚠️ ElevenLabs failed [{resp.status_code}]: {resp.text[:200]}")
        except Exception as e:
            print(f"⚠️ ElevenLabs error: {e}")

    # ── Fallback: Groq TTS ───────────────────────────────────────────────────
    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=12) as client:
                resp = await client.post(
                    GROQ_TTS_URL,
                    headers={
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type" : "application/json",
                    },
                    json={
                        "model"          : "playai-tts",
                        "input"          : text,
                        "voice"          : DEFAULT_GROQ_VOICE,
                        "response_format": "wav",
                    },
                )
            if resp.status_code == 200:
                return resp.content, "audio/wav"
            else:
                print(f"❌ Groq TTS failed [{resp.status_code}]: {resp.text[:200]}")
        except Exception as e:
            print(f"❌ Groq TTS error: {e}")

    raise HTTPException(status_code=503, detail="TTS service unavailable. Check API keys.")