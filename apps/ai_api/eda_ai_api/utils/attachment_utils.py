import os
import tempfile
from typing import Dict, Optional, Tuple

from fastapi import UploadFile
from loguru import logger

from eda_ai_api.utils.audio_utils import process_audio_file


async def process_attachment(
    attachment: Optional[UploadFile],
) -> Tuple[str, Dict]:
    """
    Process different types of attachments (audio, images, PDFs, etc.)

    Args:
        attachment: The uploaded file

    Returns:
        Tuple containing:
        - Description of the processed attachment
        - Metadata about the attachment
    """
    if not attachment:
        return "", {}

    try:
        filename = attachment.filename
        content_type = attachment.content_type or "application/octet-stream"
        size = 0

        # Save the file temporarily to get its size
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            content = await attachment.read()
            size = len(content)
            temp_file.write(content)
            temp_path = temp_file.name

        # Reset file pointer for potential reuse
        await attachment.seek(0)

        metadata = {
            "filename": filename,
            "content_type": content_type,
            "size_bytes": size,
        }

        # Process based on file type
        if content_type.startswith("audio/"):
            # Reuse existing audio processing
            transcription = await process_audio_file(attachment)
            description = f"Audio transcription: {transcription}"
            metadata["transcription"] = transcription

        elif content_type.startswith("image/"):
            description = f"Image attached: {filename} ({size} bytes)"
            # You could add image analysis here in the future

        elif content_type == "application/pdf":
            description = f"PDF document attached: {filename} ({size} bytes)"
            # You could add PDF text extraction here in the future

        elif content_type.startswith("video/"):
            description = f"Video attached: {filename} ({size} bytes)"
            # You could add video analysis here in the future

        else:
            description = (
                f"Attachment: {filename} ({content_type}, {size} bytes)"
            )

        # Clean up temp file
        os.unlink(temp_path)

        logger.info(f"Processed attachment: {filename} ({content_type})")
        return description, metadata

    except Exception as e:
        logger.error(f"Error processing attachment: {str(e)}")
        return f"Error processing attachment: {str(e)}", {"error": str(e)}
