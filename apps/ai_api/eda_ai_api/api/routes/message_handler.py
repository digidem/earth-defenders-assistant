import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from eda_config.config import ConfigLoader
from fastapi import APIRouter, File, Form, UploadFile
from loguru import logger

from eda_ai_api.agents.manager import get_agent
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines
from eda_ai_api.models.message_handler import (
    MessageHandlerResponse,
    MessageHistory,
)
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.memory import SupabaseMemory
from smolagents.local_python_executor import BASE_BUILTIN_MODULES

config = ConfigLoader.get_config()

router = APIRouter()


async def process_input_messages(
    message: Optional[str], audio: Optional[UploadFile]
) -> str:
    """Process user input from text and/or audio"""
    combined_message = []

    if audio:
        transcription = await process_audio_file(audio)
        combined_message.append(f'Transcription: "{transcription}"')

    if message:
        combined_message.append(f'Message: "{message}"')

    return "\n".join(combined_message)


async def process_message_history(
    message_history: Optional[str],
) -> List[MessageHistory]:
    """Convert message history JSON to structured objects"""
    history = []
    if message_history:
        try:
            history = [
                MessageHistory(**msg) for msg in json.loads(message_history)
            ]
        except json.JSONDecodeError:
            logger.warning("Invalid message_history JSON format")
    return history


@router.post("/handle", response_model=MessageHandlerResponse)
async def message_handler_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
    message_history: Optional[str] = Form(default=None),
    platform: Optional[str] = Form(default="whatsapp"),
) -> MessageHandlerResponse:
    """Main route handler that processes messages using the manager agent"""
    try:
        current_session = session_id or str(uuid.uuid4())
        logger.info(f"New request - Session: {current_session}")
        logger.info(f"Platform received: {platform}")

        # Process input messages (text and/or audio)
        final_message = await process_input_messages(message, audio)
        if not final_message:
            return MessageHandlerResponse(
                result="Error: No valid input provided",
                session_id=current_session,
            )

        # Process message history
        history = await process_message_history(message_history)

        # Format conversation history for the agent
        conversation_history = []
        if history:
            for msg in history:
                conversation_history.append(
                    {
                        "user": msg.human,
                        "assistant": msg.ai,
                    }
                )

        # Get current time for message formatting
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] User: {final_message}"

        # Create and configure manager agent
        agent = get_agent(platform=platform)

        # Set up the custom prompt with all required variables
        from eda_ai_api.agents.prompts.manager import MANAGER_SYSTEM_PROMPT

        agent.prompt_templates["system_prompt"] = MANAGER_SYSTEM_PROMPT.format(
            conversation_history=conversation_history,
            bot_name=config.services.whatsapp.bot_name,
            formatting_guidelines=get_formatting_guidelines(platform),
            tools=agent.tools,
            authorized_imports=BASE_BUILTIN_MODULES,
            managed_agents={},
        )

        # Run the agent with the formatted message
        response_content = agent.run(formatted_message)

        # Store conversation in Supabase could be implemented here

        # Return the agent's response
        return MessageHandlerResponse(
            result=response_content[:2499],  # Truncate if needed
            session_id=current_session,
        )

    except Exception as e:
        logger.error(f"Error in message handler route: {str(e)}")
        return MessageHandlerResponse(
            result=f"Error: {str(e)}", session_id=session_id
        )
