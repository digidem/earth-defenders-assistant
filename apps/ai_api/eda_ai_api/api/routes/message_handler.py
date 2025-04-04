import uuid
from datetime import datetime
from typing import Optional

from eda_config.config import ConfigLoader
from fastapi import APIRouter, File, Form, UploadFile
from loguru import logger

from eda_ai_api.agents.manager import get_agent
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines
from eda_ai_api.models.message_handler import MessageHandlerResponse
from eda_ai_api.utils.attachment_utils import process_attachment
from eda_ai_api.utils.memory import PocketBaseMemory
from smolagents.local_python_executor import BASE_BUILTIN_MODULES
from eda_ai_api.agents.prompts.manager import MANAGER_SYSTEM_PROMPT
from smolagents.agents import populate_template

config = ConfigLoader.get_config()

router = APIRouter()
memory = PocketBaseMemory()


@router.post("/handle", response_model=MessageHandlerResponse)
async def message_handler_route(
    message: Optional[str] = Form(default=None),
    attachment: Optional[UploadFile] = File(default=None),
    user_platform_id: Optional[str] = Form(default=None),
    platform: Optional[str] = Form(default="whatsapp"),
) -> MessageHandlerResponse:
    """Main route handler that processes messages using the manager agent"""
    try:
        current_user_id = user_platform_id or str(uuid.uuid4())
        logger.info(f"New request - User Platform ID: {current_user_id}")
        logger.info(f"Platform received: {platform}")
        logger.debug(f"Message payload: '{message}'")
        logger.debug(
            f"Attachment: {attachment.filename if attachment else None}"
        )

        # Process text message
        text_input = message or ""

        # Process attachment if present
        attachment_description = ""
        attachment_metadata = {}
        attachment_error = None

        if attachment:
            try:
                attachment_description, attachment_metadata = (
                    await process_attachment(attachment)
                )
            except Exception as e:
                attachment_error = str(e)
                logger.error(
                    f"Failed to process attachment: {attachment_error}"
                )
                # Return error response instead of continuing with empty attachment
                if not text_input:
                    return MessageHandlerResponse(
                        result=f"Desculpe, não foi possível processar seu arquivo. Erro: {attachment_error}",
                        user_platform_id=current_user_id,
                    )

        # Combine text and attachment information
        final_message = "\n".join(
            filter(
                None,
                [
                    text_input,
                    attachment_description,
                    (
                        f"[Erro ao processar anexo: {attachment_error}]"
                        if attachment_error
                        else None
                    ),
                ],
            )
        )

        if not final_message:
            logger.warning("No valid input provided")
            return MessageHandlerResponse(
                result="Error: No valid input provided (message or attachment required)",
                user_platform_id=current_user_id,
            )

        # Get conversation history from PocketBase
        conversation_history = []
        try:
            # Get history limit from config (default to 5 if not specified)
            history_limit = getattr(
                config.services.ai_api, "conversation_history_limit", 5
            )
            logger.debug(f"Using conversation history limit: {history_limit}")

            # Retrieve from PocketBase
            db_history = await memory.get_conversation_history(
                session_id=current_user_id,  # Using user_platform_id as the session key
                limit=history_limit,  # Use the configured value
            )
            conversation_history = await memory.format_history_for_context(
                db_history
            )
            logger.debug(
                f"Conversation history retrieved with {len(conversation_history)} entries"
            )
        except Exception as e:
            logger.error(
                f"Error retrieving conversation history: {str(e)}",
                exc_info=True,
            )
            # Continue without history if there's an error

        # Get current time for message formatting
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] User: {final_message}"
        logger.debug(f"Formatted message for agent: '{formatted_message}'")

        # Create and configure manager agent
        logger.debug(f"Creating agent for platform: {platform}")
        try:
            agent = get_agent(platform=platform)
            logger.debug(f"Agent created with {len(agent.tools)} tools")
        except Exception as e:
            logger.error(f"Error creating agent: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Failed to initialize agent - {str(e)}",
                user_platform_id=current_user_id,
            )

        # Set up the custom prompt with all required variables
        logger.debug("Configuring agent prompt")
        try:
            agent.prompt_templates["system_prompt"] = populate_template(
                MANAGER_SYSTEM_PROMPT,
                variables={
                    "conversation_history": conversation_history,
                    "bot_name": config.services.whatsapp.bot_name,
                    "formatting_guidelines": get_formatting_guidelines(
                        platform
                    ),
                    "tools": agent.tools,
                    "authorized_imports": BASE_BUILTIN_MODULES,
                    "managed_agents": {},
                },
            )
            logger.debug("Agent prompt configured successfully")
        except Exception as e:
            logger.error(f"Error configuring prompt: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Failed to configure agent prompt - {str(e)}",
                user_platform_id=current_user_id,
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
                user_platform_id=current_user_id,
            )

        # Store conversation in PocketBase
        try:
            await memory.add_message_to_history(
                session_id=current_user_id,  # Using user_platform_id
                user_message=final_message,
                assistant_response=response_content,
                platform=platform,
            )
            logger.info(f"Conversation stored for user {current_user_id}")
        except Exception as db_error:
            logger.error(f"Failed to store conversation: {str(db_error)}")
            # Continue even if storage fails

        # Return the agent's response
        logger.info(f"Returning response for user: {current_user_id}")
        return MessageHandlerResponse(
            result=(
                response_content[:2499]
                if response_content
                else "Error: No response generated"
            ),
            user_platform_id=current_user_id,
        )

    except Exception as e:
        logger.error(f"Error in message handler route: {str(e)}", exc_info=True)
        return MessageHandlerResponse(
            result=f"Error: {str(e)}",
            user_platform_id=user_platform_id or "error_session",
        )
