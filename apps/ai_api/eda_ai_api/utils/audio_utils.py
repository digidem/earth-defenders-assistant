import os
import tempfile
from typing import Optional

from fastapi import UploadFile

from .audio_converter import convert_ogg
from .transcriber import transcribe_audio

ALLOWED_FORMATS = {
    "audio/mpeg": "mp3",
    "audio/mp4": "mp4",
    "audio/mpga": "mpga",
    "audio/wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
}


def detect_content_type(file: UploadFile) -> Optional[str]:
    if hasattr(file, "content_type") and file.content_type:
        return file.content_type
    if hasattr(file, "mime_type") and file.mime_type:
        return file.mime_type
    ext = os.path.splitext(file.filename)[1].lower()
    return {
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".mpeg": "audio/mpeg",
        ".mpga": "audio/mpga",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
    }.get(ext)


async def process_audio_file(audio: UploadFile, language: str = "en") -> str:
    content_type = detect_content_type(audio)
    content = await audio.read()

    try:
        file_format = "mp3"
        if content_type is not None:
            file_format = ALLOWED_FORMATS.get(content_type, "mp3")

        if content_type == "audio/ogg":
            audio_path = convert_ogg(content, output_format="mp3")
        else:
            with tempfile.NamedTemporaryFile(
                suffix=f".{file_format}", delete=False
            ) as temp_file:
                temp_file.write(content)
                audio_path = temp_file.name

        return transcribe_audio(audio_path, language=language)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
