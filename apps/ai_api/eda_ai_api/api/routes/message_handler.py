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
from eda_ai_api.agents.prompts.manager import MANAGER_SYSTEM_PROMPT
from smolagents.agents import populate_template

config = ConfigLoader.get_config()

router = APIRouter()


async def process_input_messages(
    message: Optional[str], audio: Optional[UploadFile]
) -> str:
    """Process user input from text and/or audio"""
    logger.debug("Processing input messages")
    combined_message = []

    if audio:
        logger.debug(f"Processing audio file: {audio.filename}")
        transcription = await process_audio_file(audio)
        logger.info(f"Audio transcription result: '{transcription}'")
        combined_message.append(f'Transcription: "{transcription}"')

    if message:
        logger.debug(f"Processing text message: '{message}'")
        combined_message.append(f'Message: "{message}"')

    result = "\n".join(combined_message)
    logger.debug(f"Combined message: '{result}'")
    return result


async def process_message_history(
    message_history: Optional[str],
) -> List[MessageHistory]:
    """Convert message history JSON to structured objects"""
    logger.debug("Processing message history")
    history = []
    if message_history:
        try:
            parsed_history = json.loads(message_history)
            logger.debug(f"Parsed message history: {parsed_history}")
            history = [MessageHistory(**msg) for msg in parsed_history]
            logger.info(f"Processed {len(history)} message history items")
        except json.JSONDecodeError:
            logger.warning("Invalid message_history JSON format")
        except Exception as e:
            logger.error(f"Error processing message history: {str(e)}")
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
        logger.debug(f"Message payload: '{message}'")
        logger.debug(f"Audio file: {audio.filename if audio else None}")
        logger.debug(
            f"Message history length: {len(message_history) if message_history else 0}"
        )

        # Process input messages (text and/or audio)
        final_message = await process_input_messages(message, audio)
        if not final_message:
            logger.warning("No valid input provided")
            return MessageHandlerResponse(
                result="Error: No valid input provided",
                session_id=current_session,
            )

        # Process message history
        logger.debug("Getting message history")
        history = await process_message_history(message_history)

        # Format conversation history for the agent
        logger.debug("Formatting conversation history")
        conversation_history = []
        if history:
            for msg in history:
                conversation_history.append(
                    {
                        "user": msg.human,
                        "assistant": msg.ai,
                    }
                )
            logger.debug(
                f"Conversation history formatted with {len(conversation_history)} entries"
            )

        # Get current time for message formatting
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] User: {final_message}"
        logger.debug(f"Formatted message for agent: '{formatted_message}'")

        # Create and configure manager agent
        logger.debug(f"Creating agent for platform: {platform}")
        try:
            agent = get_agent(platform=platform)
            logger.debug(f"Agent created with {len(agent.tools)} tools")

            # Log available tools
            logger.debug(f"Available tools: {[tool for tool in agent.tools]}")
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Failed to initialize agent - {str(e)}",
                session_id=current_session,
            )

        # Set up the custom prompt with all required variables
        logger.debug("Configuring agent prompt")
        try:

            # Debugging the variables going into the prompt template
            logger.debug(f"Bot name: {config.services.whatsapp.bot_name}")
            logger.debug(
                f"Formatting guidelines available: {bool(get_formatting_guidelines)}"
            )
            logger.debug(f"Tools count: {len(agent.tools)}")
            logger.debug(
                f"BASE_BUILTIN_MODULES count: {len(BASE_BUILTIN_MODULES)}"
            )

            agent.prompt_templates["system_prompt"] = populate_template(
                MANAGER_SYSTEM_PROMPT,
                variables={
                    # "conversation_history": conversation_history,
                    "bot_name": config.services.whatsapp.bot_name,
                    "formatting_guidelines": get_formatting_guidelines(
                        platform
                    ),
                    "tools": agent.tools,  # Changed from agent.tools_dict to agent.tools
                    "authorized_imports": BASE_BUILTIN_MODULES,  # Add the authorized imports
                    "managed_agents": {},  # Add empty managed_agents if needed by template
                },
            )
            logger.debug("Agent prompt configured successfully")
        except Exception as e:
            logger.error(f"Error configuring prompt: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Failed to configure agent prompt - {str(e)}",
                session_id=current_session,
            )

        # Run the agent with the formatted message
        logger.info("Running agent with formatted message")
        try:
            response_content = agent.run(formatted_message)
            logger.info(
                f"Agent response received - length: {len(response_content)}"
            )
            logger.debug(
                f"Agent response: '{response_content[:100]}...'"
            )  # Log first 100 chars
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Agent execution failed - {str(e)}",
                session_id=current_session,
            )

        # Store conversation in Supabase could be implemented here
        logger.debug("Conversation storage not implemented yet")

        # Ensure response content is not None before returning
        if response_content is None:
            logger.warning("Agent returned None response")
            response_content = "Error: No response generated by the agent."

        # Return the agent's response
        logger.info(f"Returning response for session: {current_session}")
        return MessageHandlerResponse(
            result=(
                response_content[:2499]
                if response_content
                else "Error: No response generated"
            ),  # Truncate if needed
            session_id=current_session,
        )

    except Exception as e:
        logger.error(f"Error in message handler route: {str(e)}", exc_info=True)
        return MessageHandlerResponse(
            result=f"Error: {str(e)}",
            session_id=session_id or "error_session",
        )
