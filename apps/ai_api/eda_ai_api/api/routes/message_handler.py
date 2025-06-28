import uuid
from datetime import datetime
import json
from typing import Optional, List
from pydantic import BaseModel
from fastapi import APIRouter, UploadFile, File, Form
from PIL import Image
import io

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


class GroupMessageRequest(BaseModel):
    user_platform_id: str
    platform: str
    message: str
    group_id: str
    sender_name: str
    timestamp: str


@router.post("/handle", response_model=MessageHandlerResponse)
async def message_handler_route(
    message: Optional[str] = Form(None),
    user_platform_id: Optional[str] = Form(None),
    platform: str = Form("whatsapp"),
    images: List[UploadFile] = File(None),
) -> MessageHandlerResponse:
    """
    Main route handler that processes messages using the manager agent.
    Now supports image inputs for vision capabilities.
    """
    try:
        # Create MessageRequest from form fields
        request = MessageRequest(
            message=message,
            user_platform_id=user_platform_id,
            platform=platform,
        )

        current_user_id = request.user_platform_id or str(uuid.uuid4())
        logger.info(f"New request - User Platform ID: {current_user_id}")
        logger.info(f"Platform received: {request.platform}")
        logger.debug(f"Message payload: '{request.message}'")

        # Process uploaded images
        processed_images = []
        if images:
            logger.info(f"Processing {len(images)} uploaded images")
            for img_file in images:
                try:
                    # Read and convert image
                    image_bytes = await img_file.read()
                    pil_image = Image.open(io.BytesIO(image_bytes)).convert(
                        "RGB"
                    )
                    processed_images.append(pil_image)
                    logger.debug(f"Processed image: {img_file.filename}")
                except Exception as e:
                    logger.error(
                        f"Error processing image {img_file.filename}: {str(e)}"
                    )

        if not request.message:
            logger.warning("No message provided")
            return MessageHandlerResponse(
                result="Error: No message provided",
                user_platform_id=current_user_id,
            )

        # Get conversation history from vector memory with RAG
        context = {}
        try:
            context = await build_enhanced_context(
                user_platform_id=current_user_id,
                current_message=request.message,
                platform=request.platform,
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
                f"Error retrieving enhanced conversation history: {str(e)}"
            )
            conversation_history = []

        # Get current time for message formatting
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{current_time}] User: {request.message}"
        logger.debug(f"Formatted message for agent: '{formatted_message}'")

        # Create and configure manager agent with user context
        logger.debug(f"Creating agent for platform: {request.platform}")
        try:
            agent = get_agent(
                platform=request.platform,
                session_id=current_user_id,  # Pass the user session
            )
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
                        request.platform
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

        # Run the agent with the formatted message and images
        logger.info("Running agent with formatted message and images")
        try:
            response_content = agent.run(
                formatted_message,
                images=(
                    processed_images if processed_images else None
                ),  # Pass images to agent
            )
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
                user_message=request.message,
                assistant_response=response_content,
                platform=request.platform,
                metadata=None,
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
            user_platform_id=request.user_platform_id or "error_session",
        )


@router.post("/store-group-message")
async def store_group_message_route(request: GroupMessageRequest):
    """
    Store group messages in the database without processing through the agent.
    This allows the bot to maintain context of all group conversations.
    """
    try:
        logger.info(
            f"Storing group message from {request.sender_name} ({request.user_platform_id}) in group {request.group_id}"
        )

        # Format the message with sender name
        formatted_message = f"{request.sender_name}: {request.message}"

        # Store the message in vector memory for future context
        await memory.add_message_to_history(
            session_id=request.user_platform_id,
            user_message=formatted_message,  # Now includes sender name
            assistant_response="",  # No assistant response for passive storage
            platform=request.platform,
            metadata={
                "group_id": request.group_id,
                "sender_name": request.sender_name,
                "timestamp": request.timestamp,
                "message_type": "group_passive",
            },
        )

        logger.debug(
            f"Group message stored successfully for {request.user_platform_id}"
        )
        return {"success": True, "message": "Group message stored successfully"}

    except Exception as e:
        logger.error(f"Error storing group message: {str(e)}")
        return {"success": False, "error": str(e)}
