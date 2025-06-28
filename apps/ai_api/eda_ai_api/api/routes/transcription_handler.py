from fastapi import APIRouter, UploadFile, File, Form, Request, HTTPException
from pydantic import BaseModel
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.validation import validate_audio_file
from eda_ai_api.utils.error_handler import (
    log_request_info,
    handle_file_processing_error,
)
from eda_ai_api.utils.exceptions import (
    TranscriptionError,
    ValidationError,
    FileProcessingError,
)

config = ConfigLoader.get_config()

router = APIRouter()


class TranscriptionResponse(BaseModel):
    """Response model for transcription endpoint"""

    success: bool
    transcription: str
    error: str = ""
    language: str = "en"


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    request: Request, file: UploadFile = File(...), language: str = Form("en")
) -> TranscriptionResponse:
    """
    Transcribe audio file to text

    Args:
        request: FastAPI request object for logging
        file: Audio file to transcribe
        language: Language code for transcription (default: "en")

    Returns:
        TranscriptionResponse with transcription result
    """
    try:
        # Log request information
        log_request_info(
            request,
            {
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.size,
                "language": language,
            },
        )

        # Validate audio file
        validate_audio_file(file)

        # Validate language code
        if not language or len(language) != 2:
            raise ValidationError(
                "Language code must be 2 characters (e.g., 'en', 'pt')",
                "language",
            )

        logger.info(
            f"Starting audio transcription",
            extra={
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": file.size,
                "language": language,
            },
        )

        # Process audio file
        transcription = await process_audio_file(file, language=language)

        if not transcription or not transcription.strip():
            raise TranscriptionError(
                "No transcription generated from audio file", file.content_type
            )

        logger.info(
            f"Audio transcription completed successfully",
            extra={
                "filename": file.filename,
                "transcription_length": len(transcription),
                "language": language,
            },
        )

        return TranscriptionResponse(
            success=True,
            transcription=transcription,
            language=language,
        )

    except ValidationError as e:
        logger.warning(f"Transcription validation failed: {str(e)}")
        return TranscriptionResponse(
            success=False,
            transcription="",
            error=str(e),
            language=language,
        )
    except TranscriptionError as e:
        logger.error(f"Transcription failed: {str(e)}")
        return TranscriptionResponse(
            success=False,
            transcription="",
            error=str(e),
            language=language,
        )
    except Exception as e:
        logger.error(f"Unexpected transcription error: {str(e)}", exc_info=True)
        return TranscriptionResponse(
            success=False,
            transcription="",
            error=config.services.ai_api.error_messages["PROCESSING_ERROR"],
            language=language,
        )
