import os
import tempfile
from pathlib import Path
from typing import Literal

import ffmpeg

AudioFormat = Literal["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]


def convert_ogg(
    input_file: str | Path | bytes,
    output_format: AudioFormat = "mp3",
    output_path: str | Path | None = None,
) -> str:
    """
    Convert OGG audio file to another format using ffmpeg.

    Args:
        input_file: Path to input OGG file or bytes content
        output_format: Desired output format
        output_path: Optional output path. If None, uses a temporary file

    Returns:
        str: Path to the converted audio file
    """
    try:
        # Handle bytes input by writing to temp file first
        if isinstance(input_file, bytes):
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_ogg:
                temp_ogg.write(input_file)
                input_file = temp_ogg.name

        # If no output path specified, create temp file
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, f"converted_audio.{output_format}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        # Convert audio using ffmpeg
        stream = ffmpeg.input(str(input_file))
        stream = ffmpeg.output(stream, str(output_path))
        ffmpeg.run(
            stream, overwrite_output=True, capture_stdout=True, capture_stderr=True
        )

        # Clean up temp input file if we created one
        if isinstance(input_file, str) and input_file.startswith(tempfile.gettempdir()):
            os.unlink(input_file)

        return str(output_path)

    except ffmpeg.Error as e:
        raise RuntimeError(f"FFmpeg error: {e.stderr.decode()}") from e
    except Exception as e:
        raise RuntimeError(f"Error converting audio: {str(e)}") from e
