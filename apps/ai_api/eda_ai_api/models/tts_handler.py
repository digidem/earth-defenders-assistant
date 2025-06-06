from typing import Optional, Literal
from pydantic import BaseModel

# Define supported audio formats for better API documentation
AudioFormat = Literal["LINEAR16", "MP3", "OGG_OPUS", "MULAW", "ALAW"]


class TTSRequest(BaseModel):
    text: str
    language_code: Optional[str] = None
    voice_name: Optional[str] = None
    audio_encoding: Optional[AudioFormat] = (
        None  # Add the missing audio_encoding field
    )
    pitch: Optional[float] = None
    speaking_rate: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "text": "Olá, como você está hoje?",
                "language_code": "pt-BR",
                "voice_name": "pt-BR-Chirp3-HD-Achernar",
                "audio_encoding": "OGG_OPUS",
                "pitch": 0.0,
                "speaking_rate": 1.0,
            }
        }


class TTSResponse(BaseModel):
    success: bool
    audio_path: Optional[str] = None
    error: Optional[str] = None
    message: str = ""

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "audio_path": "/tmp/tmpwsgnjvyf.ogg",
                "error": None,
                "message": "Audio generated successfully",
            }
        }


class TTSVoice(BaseModel):
    """Model for voice information"""

    name: str
    gender: str


class VoicesResponse(BaseModel):
    """Response model for available voices"""

    success: bool
    voices: list[tuple[str, str]]
    error: Optional[str] = None


class AudioFormatInfo(BaseModel):
    """Information about supported audio formats"""

    format: str
    extension: str
    description: str
    quality: str


class FormatsResponse(BaseModel):
    """Response model for supported formats"""

    success: bool
    formats: list[AudioFormatInfo]
