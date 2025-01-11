import json
import os
from typing import Optional, List, Dict
import uuid
from fastapi import APIRouter, File, Form, UploadFile
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from loguru import logger
import httpx

from eda_ai_api.models.classifier import ClassifierResponse, MessageHistory
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.memory import SupabaseMemory, Mem0ConversationManager
from eda_ai_api.utils.prompts import (
    ROUTER_TEMPLATE,
    INSUFFICIENT_TEMPLATES,
    PROPOSAL_TEMPLATE,
    TOPIC_TEMPLATE,
)

router = APIRouter()
# Disabled Mem0 memory manager
# mem0_manager = Mem0ConversationManager()

# Setup LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),  # Use environment variable
    temperature=0.5,
)


async def process_discovery(message: str, context: str) -> Dict[str, str]:
    """Process discovery requests"""
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
        api_response = await client.post(
            "http://127.0.0.1:8083/api/grant/discovery", json={"topics": topics}
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


@router.post("/classify", response_model=ClassifierResponse)
async def classifier_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
    message_history: Optional[str] = Form(default=None),
) -> ClassifierResponse:
    """Main route handler"""
    try:
        current_session = session_id or str(uuid.uuid4())
        logger.info(f"New request - Session: {current_session}")

        # Initialize/get Mem0 session - Disabled
        # current_session = await mem0_manager.get_or_create_session(session_id=current_session)

        # Process inputs
        combined_message = []
        if audio:
            transcription = await process_audio_file(audio)
            combined_message.append(f'Transcription: "{transcription}"')
        if message:
            combined_message.append(f'Message: "{message}"')

        if not combined_message:
            return ClassifierResponse(result="Error: No valid input provided")

        # Get conversation history from Supabase
        history = []
        if message_history:
            try:
                history = [MessageHistory(**msg) for msg in json.loads(message_history)]
            except json.JSONDecodeError:
                logger.warning("Invalid message_history JSON format")

        # Get context from Supabase only
        supabase_context = SupabaseMemory.format_history(history)
        final_message = "\n".join(combined_message)
        decision = await route_message(final_message, supabase_context)
        logger.info(f"Routing decision: {decision}")

        # Process based on route
        if decision == "discovery":
            response = await process_discovery(final_message, supabase_context)
        elif decision == "heartbeat":
            response = {"result": "*Yes, I'm here! 🟢*\n_Ready to help you!_"}
        else:
            response = {"result": f"Service '{decision}' not implemented yet"}

        result = response["result"]
        if len(result) > 2499:
            result = result[:2499]

        # Disabled Mem0 storage
        # await mem0_manager.add_conversation(
        #     session_id=current_session,
        #     user_message=final_message,
        #     assistant_response=result,
        # )

        return ClassifierResponse(result=result, session_id=current_session)

    except Exception as e:
        logger.error(f"Error in classifier route: {str(e)}")
        return ClassifierResponse(result=f"Error: {str(e)}")
