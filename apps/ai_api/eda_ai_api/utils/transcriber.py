from groq import Groq
from loguru import logger
from eda_config.config import ConfigLoader

config = ConfigLoader.get_config()


def transcribe_audio(audio_path: str, language: str = "en") -> str:
    """
    Transcribe audio file using Groq's Whisper API.

    Args:
        audio_path: Path to the audio file
        language: Language code (default: "en")

    Returns:
        str: Transcribed text
    """
    try:
        # Create client with API key from config
        client = Groq(api_key=config.api_keys.groq)

        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3-turbo",
                response_format="json",
                # language=language,
                temperature=0.0,
            )

            logger.info(f"Transcription result: {transcription.text}")
            return transcription.text

    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise RuntimeError(f"Transcription failed: {str(e)}") from e
