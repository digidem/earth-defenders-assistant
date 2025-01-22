import json
import uuid
from typing import Dict, Optional

import httpx
from eda_config.config import ConfigLoader  # Add this import
from fastapi import APIRouter, File, Form, UploadFile
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from loguru import logger

from eda_ai_api.models.classifier import ClassifierResponse, MessageHistory
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.memory import SupabaseMemory
from eda_ai_api.utils.prompts import (
    INSUFFICIENT_TEMPLATES,
    ROUTER_TEMPLATE,
    TOPIC_TEMPLATE,
)

config = ConfigLoader.get_config()  # Add this line

router = APIRouter()
# Disabled Mem0 memory manager
# mem0_manager = Mem0ConversationManager()

# Update LLM configuration
llm = ChatGroq(
    model=config.ai_models["premium"].model,
    api_key=config.api_keys.groq,
    temperature=config.ai_models["premium"].temperature,
)


async def process_discovery(
    message: str, context: str, platform: Optional[str] = "default"
) -> Dict[str, str]:
    """Process discovery requests"""
    # Ensure platform is never None
    actual_platform = platform or "default"

    response = llm.invoke(
        [HumanMessage(content=TOPIC_TEMPLATE.format(context=context, message=message))]
    )
    topics = [t.strip() for t in response.content.split(",") if t.strip()][:5]
    logger.info(f"Extracted Topics: {topics}")

    if not topics or topics == ["INSUFFICIENT_CONTEXT"]:
        return {
            "result": INSUFFICIENT_TEMPLATES["discovery"].format(
                context=context, message=message
            )
        }

    async with httpx.AsyncClient() as client:
        logger.info("Calling discovery API...")
        discovery_port = config.ports.ai_api
        api_response = await client.post(
            f"http://127.0.0.1:{discovery_port}/api/grant/discovery",
            json={"topics": topics, "platform": actual_platform},
        )
        logger.info(f"Discovery API Response: {api_response.json()}")
        return {"result": str(api_response.json())}


async def route_message(message: str, context: str) -> str:
    """Route message to appropriate handler"""
    logger.info(f"\n=== Routing Message ===\nContext: {context}\nMessage: {message}")

    response = llm.invoke(
        [HumanMessage(content=ROUTER_TEMPLATE.format(message=message))]
    )
    decision = response.content.lower().strip()
    logger.info(f"Router Decision: {decision}")
    return decision


async def process_input_messages(
    message: Optional[str], audio: Optional[UploadFile]
) -> list[str]:
    combined_message = []
    if audio:
        transcription = await process_audio_file(audio)
        combined_message.append(f'Transcription: "{transcription}"')
    if message:
        combined_message.append(f'Message: "{message}"')
    return combined_message


async def process_message_history(
    message_history: Optional[str],
) -> list[MessageHistory]:
    history = []
    if message_history:
        try:
            history = [MessageHistory(**msg) for msg in json.loads(message_history)]
        except json.JSONDecodeError:
            logger.warning("Invalid message_history JSON format")
    return history


@router.post("/classify", response_model=ClassifierResponse)
async def classifier_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
    message_history: Optional[str] = Form(default=None),
    platform: Optional[str] = Form(default="default"),
) -> ClassifierResponse:
    """Main route handler"""
    try:
        current_session = session_id or str(uuid.uuid4())
        logger.info(f"New request - Session: {current_session}")
        logger.info(f"Platform received: {platform}")  # Add this line

        # Initialize/get Mem0 session - Disabled
        # current_session = await mem0_manager.get_or_create_session(session_id=current_session)

        combined_message = await process_input_messages(message, audio)
        if not combined_message:
            return ClassifierResponse(result="Error: No valid input provided")

        history = await process_message_history(message_history)
        supabase_context = SupabaseMemory.format_history(history)

        final_message = "\n".join(combined_message)
        decision = await route_message(final_message, supabase_context)
        logger.info(f"Processing {decision} request for platform: {platform}")

        response = await process_route_decision(
            decision, final_message, supabase_context, platform
        )
        result = response["result"][:2499]  # Truncate if needed

        return ClassifierResponse(result=result, session_id=current_session)

    except Exception as e:
        logger.error(f"Error in classifier route: {str(e)}")
        return ClassifierResponse(result=f"Error: {str(e)}")


async def process_route_decision(
    decision: str, message: str, context: str, platform: Optional[str]
) -> Dict[str, str]:
    if decision == "discovery":
        response = await process_discovery(message, context, platform or "default")
        logger.info(f"Discovery response for platform {platform}: {response}")
    elif decision == "heartbeat":
        response = {"result": "*Yes, I'm here! 🟢*\n_Ready to help you!_"}
    else:
        response = {"result": f"Service '{decision}' not implemented yet"}

    return response
