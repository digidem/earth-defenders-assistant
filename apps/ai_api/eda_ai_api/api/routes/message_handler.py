import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form
from loguru import logger

from eda_config.config import ConfigLoader
from eda_ai_api.agents.manager import get_agent
from eda_ai_api.agents.prompts.formatting import get_formatting_guidelines
from eda_ai_api.models.message_handler import MessageHandlerResponse
from eda_ai_api.utils.context_builder import build_enhanced_context
from eda_ai_api.utils.vector_memory import VectorMemory
from eda_ai_api.utils.attachment_utils import process_attachment
from smolagents.local_python_executor import BASE_BUILTIN_MODULES
from eda_ai_api.agents.prompts.manager import MANAGER_SYSTEM_PROMPT
from smolagents.agents import populate_template

config = ConfigLoader.get_config()

router = APIRouter()
memory = VectorMemory()


class MessageRequest(BaseModel):
    message: Optional[str] = None
    user_platform_id: Optional[str] = None
    platform: str = "whatsapp"


@router.post("/handle", response_model=MessageHandlerResponse)
async def message_handler_route(
    message: Optional[str] = Form(None),
    user_platform_id: Optional[str] = Form(None),
    platform: str = Form("whatsapp"),
    attachment: Optional[UploadFile] = File(None),
    language: str = Form("pt"),  # Default to Portuguese, adjust as needed
) -> MessageHandlerResponse:
    """
    Main route handler that processes messages and optional attachments using the manager agent.
    """
    try:
        current_user_id = user_platform_id or str(uuid.uuid4())
        logger.info(f"New request - User Platform ID: {current_user_id}")
        logger.info(f"Platform received: {platform}")
        logger.debug(f"Message payload: '{message}'")

        # Process attachment if present
        attachment_description = ""
        attachment_metadata = {}
        if attachment:
            logger.info(
                f"Processing attachment: {attachment.filename} ({attachment.content_type})"
            )
            attachment_description, attachment_metadata = (
                await process_attachment(attachment)
            )
            logger.info(f"Attachment processed: {attachment_description}")

        # Combine text and attachment description for agent input
        text_input = message or ""
        if attachment_description:
            text_input = f"{text_input}\n\n{attachment_description}".strip()

        if not text_input:
            logger.warning("No valid input provided")
            return MessageHandlerResponse(
                result="Error: No valid input provided (message or attachment required)",
                user_platform_id=current_user_id,
            )

        # Get conversation history from vector memory with RAG
        context = {}
        try:
            context = await build_enhanced_context(
                user_platform_id=current_user_id,
                current_message=text_input,
                platform=platform,
                recent_history_limit=config.services.ai_api.conversation_history_limit,
                relevant_history_limit=config.services.ai_api.relevant_history_limit,
                cross_session=False,
            )
            conversation_history = context.get("merged_history", [])
            logger.debug(
                f"Enhanced conversation context built with {len(context.get('recent_history', []))} recent "
                f"and {len(context.get('relevant_history', []))} relevant exchanges"
            )
        except Exception as e:
            logger.error(
                f"Error retrieving enhanced conversation history: {str(e)}",
                exc_info=True,
            )
            conversation_history = []

        # Get current time for message formatting
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] User: {text_input}"
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
                    "managed_agents": agent.managed_agents,
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
            logger.debug(f"Agent response: '{response_content[:100]}...'")
        except Exception as e:
            logger.error(f"Error running agent: {str(e)}", exc_info=True)
            return MessageHandlerResponse(
                result=f"Error: Agent execution failed - {str(e)}",
                user_platform_id=current_user_id,
            )

        # Store conversation in vector memory
        try:
            await memory.add_message_to_history(
                session_id=current_user_id,
                user_message=text_input,
                assistant_response=response_content,
                platform=platform,
                metadata=attachment_metadata if attachment_metadata else None,
            )
            logger.info(f"Conversation stored for user {current_user_id}")
        except Exception as db_error:
            logger.error(f"Failed to store conversation: {str(db_error)}")

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
