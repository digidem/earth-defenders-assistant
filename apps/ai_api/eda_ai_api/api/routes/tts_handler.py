import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from loguru import logger
from typing import Optional

from eda_ai_api.models.tts_handler import (
    TTSRequest,
    TTSResponse,
    VoicesResponse,
    FormatsResponse,
    AudioFormatInfo,
)
from eda_ai_api.utils.tts_service import TTSService

router = APIRouter()


def get_tts_service():
    """Get TTS service instance - lazy initialization"""
    return TTSService()


@router.post(
    "/generate",
    response_model=TTSResponse,
    summary="Generate speech from text",
    description="Generate speech audio from text using Google Cloud TTS. Returns file path for download.",
    response_description="TTS generation result with file path",
)
async def generate_speech(request: TTSRequest) -> TTSResponse:
    """
    Generate speech from text using Google Cloud TTS

    Args:
        request: TTS request containing text and optional voice parameters

    Returns:
        TTSResponse with success status and audio file path
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        tts_service = get_tts_service()

        # Generate audio file
        audio_path = await tts_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            audio_encoding=request.audio_encoding,
            pitch=request.pitch,
            speaking_rate=request.speaking_rate,
        )

        return TTSResponse(
            success=True,
            audio_path=audio_path,
            message="Audio generated successfully",
        )

    except Exception as e:
        logger.error(f"TTS generation failed: {str(e)}")
        return TTSResponse(
            success=False, error=str(e), message="Failed to generate audio"
        )


@router.get(
    "/download/{filename}",
    summary="Download generated audio file",
    description="Download a previously generated audio file by filename",
    response_description="Audio file download",
)
async def download_audio(filename: str):
    """
    Download generated audio file

    Args:
        filename: Name of the audio file to download

    Returns:
        FileResponse with the audio file
    """
    try:
        # For security, only allow files from temp directory
        if not filename.startswith("/tmp/") and not filename.startswith("tmp"):
            # Construct full path if just filename provided
            import tempfile

            file_path = os.path.join(tempfile.gettempdir(), filename)
        else:
            file_path = filename

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Audio file not found")

        # Determine media type based on file extension
        media_type_map = {
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg",
        }

        file_ext = os.path.splitext(file_path)[1].lower()
        media_type = media_type_map.get(file_ext, "audio/mpeg")

        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=os.path.basename(file_path),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading audio file: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error downloading audio file"
        )


@router.post(
    "/generate-and-download",
    summary="Generate and immediately download audio",
    description="Generate speech from text and immediately return the audio file for download",
    response_description="Audio file download",
)
async def generate_and_download(request: TTSRequest):
    """
    Generate speech and immediately return the audio file for download

    Args:
        request: TTS request containing text and optional voice parameters including audio_encoding

    Returns:
        FileResponse with the generated audio file
    """
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text is required")

        tts_service = get_tts_service()

        # Generate audio file
        audio_path = await tts_service.text_to_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            audio_encoding=request.audio_encoding,  # Now properly documented
            pitch=request.pitch,
            speaking_rate=request.speaking_rate,
        )

        # Determine media type based on file extension
        media_type_map = {
            ".wav": "audio/wav",
            ".mp3": "audio/mpeg",
            ".ogg": "audio/ogg",
        }

        file_ext = os.path.splitext(audio_path)[1].lower()
        media_type = media_type_map.get(file_ext, "audio/mpeg")

        return FileResponse(
            path=audio_path,
            media_type=media_type,
            filename=f"tts_audio_{os.path.basename(audio_path)}",
        )

    except Exception as e:
        logger.error(f"TTS generation and download failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate audio: {str(e)}"
        )


@router.get(
    "/voices",
    response_model=VoicesResponse,
    summary="Get available TTS voices",
    description="Retrieve list of available voices for text-to-speech generation",
    response_description="List of available voices with gender information",
)
async def get_available_voices(
    language_code: Optional[str] = Query(
        None,
        description="Optional language code to filter voices (e.g., 'pt-BR', 'en-US')",
        example="pt-BR",
    )
):
    """
    Get list of available voices for TTS

    Args:
        language_code: Optional language code to filter voices

    Returns:
        List of available voices with gender information
    """
    try:
        tts_service = get_tts_service()
        voices = tts_service.get_available_voices(language_code)
        return VoicesResponse(success=True, voices=voices)
    except Exception as e:
        logger.error(f"Error getting voices: {str(e)}")
        return VoicesResponse(success=False, voices=[], error=str(e))


@router.get(
    "/formats",
    response_model=FormatsResponse,
    summary="Get supported audio formats",
    description="Retrieve list of supported audio formats for TTS generation",
    response_description="List of supported audio formats with details",
)
async def get_supported_formats():
    """
    Get list of supported audio formats

    Returns:
        List of supported audio formats with descriptions and quality info
    """
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

    return FormatsResponse(success=True, formats=formats)
