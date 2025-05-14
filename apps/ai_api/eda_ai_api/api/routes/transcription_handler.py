from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from eda_ai_api.utils.audio_utils import process_audio_file
from loguru import logger

router = APIRouter()


class TranscriptionResponse(BaseModel):
    success: bool
    transcription: str
    error: str = ""


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    file: UploadFile = File(...), language: str = Form("en")
):
    try:
        transcription = await process_audio_file(file, language=language)
        return TranscriptionResponse(success=True, transcription=transcription)
    except Exception as e:
        logger.error(f"Transcription failed: {str(e)}")
        return TranscriptionResponse(
            success=False, transcription="", error=str(e)
        )
