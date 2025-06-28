import tempfile
import os
from typing import Optional, List, Tuple
from google.cloud import texttospeech
from google.oauth2 import service_account
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.utils.exceptions import (
    TTSGenerationError,
    ServiceUnavailableError,
    ValidationError,
)

config = ConfigLoader.get_config()


class TTSService:
    """Text-to-Speech service using Google Cloud TTS with improved error handling"""

    def __init__(self):
        """Initialize TTS service with configuration"""
        self.client = None
        self.tts_config = config.services.tts
        self.credentials_available = self._check_credentials()

    def _check_credentials(self) -> bool:
        """
        Check if Google Cloud credentials are available

        Returns:
            bool: True if credentials are available, False otherwise
        """
        try:
            # First try to use service account from config
            service_account_path = (
                config.api_keys.google_cloud.service_account_path
            )
            if service_account_path and os.path.exists(service_account_path):
                logger.debug("Google Cloud service account found")
                return True

            # Fallback to default credentials
            import google.auth

            google.auth.default()
            logger.debug("Google Cloud default credentials found")
            return True
        except Exception as e:
            logger.warning(f"Google Cloud credentials not available: {str(e)}")
            return False

    def _get_client(self) -> texttospeech.TextToSpeechClient:
        """
        Get or create TTS client with lazy initialization

        Returns:
            TextToSpeechClient: Configured TTS client

        Raises:
            ServiceUnavailableError: If TTS service is not available
        """
        if not self.credentials_available:
            raise ServiceUnavailableError(
                "Google Cloud TTS",
                "Google Cloud credentials not configured. Please set up authentication.",
            )

        if self.client is None:
            try:
                # Try to use service account from config first
                service_account_path = (
                    config.api_keys.google_cloud.service_account_path
                )
                if service_account_path and os.path.exists(
                    service_account_path
                ):
                    credentials = (
                        service_account.Credentials.from_service_account_file(
                            service_account_path
                        )
                    )
                    self.client = texttospeech.TextToSpeechClient(
                        credentials=credentials
                    )
                    logger.info(
                        "Google Cloud TTS client initialized with service account"
                    )
                else:
                    # Fallback to default credentials
                    self.client = texttospeech.TextToSpeechClient()
                    logger.info(
                        "Google Cloud TTS client initialized with default credentials"
                    )

            except Exception as e:
                logger.error(
                    f"Failed to initialize Google Cloud TTS client: {str(e)}"
                )
                raise ServiceUnavailableError("Google Cloud TTS", str(e))

        return self.client

    def _get_encoding_and_extension(
        self, encoding_name: str
    ) -> Tuple[texttospeech.AudioEncoding, str]:
        """
        Get the proper encoding enum and file extension for audio format

        Args:
            encoding_name: Audio encoding name string

        Returns:
            Tuple of (AudioEncoding enum, file extension)
        """
        encoding_map = {
            "LINEAR16": (texttospeech.AudioEncoding.LINEAR16, ".wav"),
            "MP3": (texttospeech.AudioEncoding.MP3, ".mp3"),
            "OGG_OPUS": (texttospeech.AudioEncoding.OGG_OPUS, ".ogg"),
            "MULAW": (texttospeech.AudioEncoding.MULAW, ".wav"),
            "ALAW": (texttospeech.AudioEncoding.ALAW, ".wav"),
        }

        if encoding_name not in encoding_map:
            logger.warning(
                f"Unknown encoding '{encoding_name}', defaulting to MP3"
            )
            encoding_name = "MP3"

        return encoding_map[encoding_name]

    async def text_to_speech(
        self,
        text: str,
        language_code: Optional[str] = None,
        voice_name: Optional[str] = None,
        audio_encoding: Optional[str] = None,
        pitch: Optional[float] = None,
        speaking_rate: Optional[float] = None,
        effects_profile_id: Optional[List[str]] = None,
    ) -> str:
        """
        Convert text to speech and return path to audio file

        Args:
            text: Text to convert to speech
            language_code: Language code (defaults to config)
            voice_name: Specific voice to use (defaults to config)
            audio_encoding: Output audio format string (defaults to config)
            pitch: Voice pitch adjustment (defaults to config)
            speaking_rate: Speech rate adjustment (defaults to config)
            effects_profile_id: Audio effects profile (defaults to config)

        Returns:
            str: Path to generated audio file

        Raises:
            TTSGenerationError: If TTS generation fails
            ValidationError: If input parameters are invalid
        """
        try:
            # Validate input text
            if not text or not text.strip():
                raise ValidationError("Text cannot be empty", "text")

            if len(text) > 5000:
                raise ValidationError(
                    "Text too long. Maximum 5000 characters", "text"
                )

            client = self._get_client()

            # Use config defaults if not specified
            language_code = language_code or self.tts_config.language_code
            voice_name = voice_name or self.tts_config.voice_name
            pitch = pitch if pitch is not None else self.tts_config.pitch
            speaking_rate = (
                speaking_rate
                if speaking_rate is not None
                else self.tts_config.speaking_rate
            )
            effects_profile_id = (
                effects_profile_id or self.tts_config.effects_profile_id
            )

            # Set audio encoding based on config or parameter
            encoding_name = audio_encoding or self.tts_config.audio_encoding
            audio_encoding_enum, file_extension = (
                self._get_encoding_and_extension(encoding_name)
            )

            logger.debug(
                f"TTS parameters configured",
                extra={
                    "language_code": language_code,
                    "voice_name": voice_name,
                    "encoding": encoding_name,
                    "pitch": pitch,
                    "speaking_rate": speaking_rate,
                    "text_length": len(text),
                },
            )

            # Construct the request
            input_text = texttospeech.SynthesisInput(text=text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code, name=voice_name
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=audio_encoding_enum,
                pitch=pitch,
                speaking_rate=speaking_rate,
                effects_profile_id=effects_profile_id,
            )

            # Perform the text-to-speech request
            response = client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            # Save to temporary file with correct extension
            with tempfile.NamedTemporaryFile(
                suffix=file_extension, delete=False
            ) as temp_file:
                temp_file.write(response.audio_content)
                audio_path = temp_file.name

            logger.info(
                f"TTS audio generated successfully",
                extra={
                    "audio_path": audio_path,
                    "format": encoding_name,
                    "file_size": len(response.audio_content),
                    "text_length": len(text),
                },
            )

            return audio_path

        except ValidationError:
            raise
        except ServiceUnavailableError:
            raise
        except Exception as e:
            logger.error(f"TTS generation failed: {str(e)}", exc_info=True)
            raise TTSGenerationError(
                f"TTS generation failed: {str(e)}", len(text)
            )

    def get_available_voices(
        self, language_code: Optional[str] = None
    ) -> List[Tuple[str, str]]:
        """
        Get list of available voices

        Args:
            language_code: Optional language code to filter voices

        Returns:
            List of (voice_name, gender) tuples
        """
        try:
            client = self._get_client()
            voices = client.list_voices(language_code=language_code)

            voice_list = [
                (voice.name, voice.ssml_gender.name) for voice in voices.voices
            ]

            logger.info(
                f"Retrieved available voices",
                extra={
                    "language_code": language_code,
                    "voice_count": len(voice_list),
                },
            )

            return voice_list

        except Exception as e:
            logger.error(f"Failed to get voices: {str(e)}", exc_info=True)
            return []
