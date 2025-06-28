import os
import tempfile
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.models.tts_handler import (
    TTSRequest,
    TTSResponse,
    VoicesResponse,
    FormatsResponse,
    AudioFormatInfo,
)
from eda_ai_api.utils.tts_service import TTSService
from eda_ai_api.utils.validation import (
    validate_tts_parameters,
    validate_file_path,
)
from eda_ai_api.utils.error_handler import (
    handle_file_processing_error,
    log_request_info,
    create_error_response,
)
from eda_ai_api.utils.exceptions import (
    ValidationError,
    TTSGenerationError,
    FileProcessingError,
)

config = ConfigLoader.get_config()

router = APIRouter()


def get_tts_service() -> TTSService:
    """Get TTS service instance with lazy initialization"""
    return TTSService()


@router.post(
    "/generate",
    response_model=TTSResponse,
    summary="Generate speech from text",
    description="Generate speech audio from text using Google Cloud TTS. Returns file path for download.",
    response_description="TTS generation result with file path",
)
async def generate_speech(
    request: Request, tts_request: TTSRequest
) -> TTSResponse:
    """
    Generate speech from text using Google Cloud TTS

    Args:
        request: FastAPI request object for logging
        tts_request: TTS request containing text and optional voice parameters

    Returns:
        TTSResponse with success status and audio file path
    """
    try:
        # Log request information
        log_request_info(request, {"text_length": len(tts_request.text)})

        # Validate TTS parameters
        validate_tts_parameters(
            text=tts_request.text,
            language_code=tts_request.language_code,
            voice_name=tts_request.voice_name,
            pitch=tts_request.pitch,
            speaking_rate=tts_request.speaking_rate,
        )

        tts_service = get_tts_service()

        # Generate audio file
        audio_path = await tts_service.text_to_speech(
            text=tts_request.text,
            language_code=tts_request.language_code,
            voice_name=tts_request.voice_name,
            audio_encoding=tts_request.audio_encoding,
            pitch=tts_request.pitch,
            speaking_rate=tts_request.speaking_rate,
        )

        logger.info(
            f"TTS audio generated successfully",
            extra={
                "text_length": len(tts_request.text),
                "audio_path": audio_path,
                "audio_encoding": tts_request.audio_encoding,
            },
        )

        return TTSResponse(
            success=True,
            audio_path=audio_path,
            message=config.services.ai_api.success_messages["AUDIO_GENERATED"],
        )

    except ValidationError as e:
        logger.warning(f"TTS validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except TTSGenerationError as e:
        logger.error(f"TTS generation failed: {str(e)}")
        return TTSResponse(
            success=False,
            error=str(e),
            message=config.services.ai_api.error_messages["PROCESSING_ERROR"],
        )
    except Exception as e:
        logger.error(f"Unexpected TTS error: {str(e)}", exc_info=True)
        return TTSResponse(
            success=False,
            error=config.services.ai_api.error_messages["SERVICE_UNAVAILABLE"],
            message=config.services.ai_api.error_messages[
                "SERVICE_UNAVAILABLE"
            ],
        )


@router.get(
    "/download/{filename}",
    summary="Download generated audio file",
    description="Download a previously generated audio file by filename",
    response_description="Audio file download",
)
async def download_audio(request: Request, filename: str) -> FileResponse:
    """
    Download generated audio file

    Args:
        request: FastAPI request object for logging
        filename: Name of the audio file to download

    Returns:
        FileResponse with the audio file
    """
    try:
        log_request_info(request, {"filename": filename})

        # Validate filename for security
        if (
            not filename
            or len(filename) > config.services.ai_api.max_filename_length
        ):
            raise HTTPException(status_code=400, detail="Invalid filename")

        # Construct safe file path
        if not filename.startswith(config.services.ai_api.temp_dir_prefix):
            # Construct full path if just filename provided
            file_path = os.path.join(tempfile.gettempdir(), filename)
        else:
            file_path = filename

        # Validate file path for security
        validate_file_path(file_path)

        # Determine media type based on file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        media_type = config.services.ai_api.media_type_map.get(
            file_ext, "audio/mpeg"
        )

        logger.info(
            f"Audio file download requested",
            extra={
                "filename": filename,
                "file_path": file_path,
                "media_type": media_type,
            },
        )

        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio file: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=config.services.ai_api.error_messages["FILE_NOT_FOUND"],
        )


@router.post(
    "/generate-and-download",
    summary="Generate and immediately download audio",
    description="Generate speech from text and immediately return the audio file for download",
    response_description="Audio file download",
)
async def generate_and_download(
    request: Request, tts_request: TTSRequest
) -> FileResponse:
    """
    Generate speech and immediately return the audio file for download

    Args:
        request: FastAPI request object for logging
        tts_request: TTS request containing text and optional voice parameters

    Returns:
        FileResponse with the generated audio file
    """
    try:
        log_request_info(request, {"text_length": len(tts_request.text)})

        # Validate TTS parameters
        validate_tts_parameters(
            text=tts_request.text,
            language_code=tts_request.language_code,
            voice_name=tts_request.voice_name,
            pitch=tts_request.pitch,
            speaking_rate=tts_request.speaking_rate,
        )

        tts_service = get_tts_service()

        # Generate audio file
        audio_path = await tts_service.text_to_speech(
            text=tts_request.text,
            language_code=tts_request.language_code,
            voice_name=tts_request.voice_name,
            audio_encoding=tts_request.audio_encoding,
            pitch=tts_request.pitch,
            speaking_rate=tts_request.speaking_rate,
        )

        # Determine media type based on file extension
        file_ext = os.path.splitext(audio_path)[1].lower()
        media_type = config.services.ai_api.media_type_map.get(
            file_ext, "audio/mpeg"
        )

        logger.info(
            f"TTS audio generated and ready for download",
            extra={
                "text_length": len(tts_request.text),
                "audio_path": audio_path,
                "media_type": media_type,
            },
        )

        return FileResponse(
            path=audio_path,
            media_type=media_type,
            filename=f"tts_audio_{os.path.basename(audio_path)}",
        )

    except ValidationError as e:
        logger.warning(f"TTS validation failed: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except TTSGenerationError as e:
        logger.error(f"TTS generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate audio: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected TTS error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=config.services.ai_api.error_messages["SERVICE_UNAVAILABLE"],
        )


@router.get(
    "/voices",
    response_model=VoicesResponse,
    summary="Get available TTS voices",
    description="Retrieve list of available voices for text-to-speech generation",
    response_description="List of available voices with gender information",
)
async def get_available_voices(
    request: Request,
    language_code: Optional[str] = Query(
        None,
        description="Optional language code to filter voices (e.g., 'pt-BR', 'en-US')",
        example="pt-BR",
    ),
) -> VoicesResponse:
    """
    Get list of available voices for TTS

    Args:
        request: FastAPI request object for logging
        language_code: Optional language code to filter voices

    Returns:
        List of available voices with gender information
    """
    try:
        log_request_info(request, {"language_code": language_code})

        tts_service = get_tts_service()
        voices = tts_service.get_available_voices(language_code)

        logger.info(
            f"Retrieved available voices",
            extra={
                "language_code": language_code,
                "voice_count": len(voices),
            },
        )

        return VoicesResponse(success=True, voices=voices)
    except Exception as e:
        logger.error(f"Error getting voices: {str(e)}", exc_info=True)
        return VoicesResponse(
            success=False,
            voices=[],
            error=config.services.ai_api.error_messages["SERVICE_UNAVAILABLE"],
        )


@router.get(
    "/formats",
    response_model=FormatsResponse,
    summary="Get supported audio formats",
    description="Retrieve list of supported audio formats for TTS generation",
    response_description="List of supported audio formats with details",
)
async def get_supported_formats(request: Request) -> FormatsResponse:
    """
    Get list of supported audio formats

    Args:
        request: FastAPI request object for logging

    Returns:
        List of supported audio formats with descriptions and quality info
    """
    log_request_info(request)

    formats = [
        AudioFormatInfo(
            format="LINEAR16",
            extension=".wav",
            description="16-bit Linear PCM (WAV format)",
            quality="High",
        ),
        AudioFormatInfo(
            format="MP3",
            extension=".mp3",
            description="MP3 audio format",
            quality="Good",
        ),
        AudioFormatInfo(
            format="OGG_OPUS",
            extension=".ogg",
            description="Ogg Opus format (efficient compression)",
            quality="High",
        ),
        AudioFormatInfo(
            format="MULAW",
            extension=".wav",
            description="8-bit μ-law PCM",
            quality="Low",
        ),
        AudioFormatInfo(
            format="ALAW",
            extension=".wav",
            description="8-bit A-law PCM",
            quality="Low",
        ),
    ]

    logger.info(
        f"Retrieved supported audio formats",
        extra={"format_count": len(formats)},
    )
    return FormatsResponse(success=True, formats=formats)
