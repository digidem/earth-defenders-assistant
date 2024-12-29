import json
import os
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, File, Form, UploadFile
from llama_index.core import PromptTemplate
from llama_index.llms.groq import Groq
from loguru import logger
from onboarding.crew import OnboardingCrew
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

from eda_ai_api.models.classifier import ClassifierResponse, MessageHistory
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.memory import ZepConversationManager
from eda_ai_api.utils.prompts import (
    INSUFFICIENT_TEMPLATES,
    PROPOSAL_TEMPLATE,
    RESPONSE_PROCESSOR_TEMPLATE,
    TOPIC_TEMPLATE,
)

router = APIRouter()

# Setup LLM
llm = Groq(
    model="llama-3.3-70b-versatile",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)


async def extract_topics(message: str, history: list) -> list[str]:
    """Extract topics with conversation context"""
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    response = llm.complete(TOPIC_TEMPLATE.format(context=context, message=message))
    if response.text.strip() == "INSUFFICIENT_CONTEXT":
        return ["INSUFFICIENT_CONTEXT"]
    topics = [t.strip() for t in response.text.split(",") if t.strip()][:5]
    return topics if topics else ["INSUFFICIENT_CONTEXT"]


async def extract_proposal_details(message: str, history: list) -> tuple[str, str]:
    """Extract project and grant details with conversation context"""
    context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    response = llm.complete(PROPOSAL_TEMPLATE.format(context=context, message=message))
    extracted = response.text.split("|")
    community_project = extracted[0].strip() if len(extracted) > 0 else "unknown"
    grant_call = extracted[1].strip() if len(extracted) > 1 else "unknown"
    return community_project, grant_call


async def process_llm_response(message: str, response: str) -> str:
    processed = llm.complete(
        RESPONSE_PROCESSOR_TEMPLATE.format(original_message=message, response=response)
    )
    logger.info(f"Processed response: {processed.text}")
    return processed.text


async def process_decision(
    decision: str,
    message: str,
    zep_history: list,
    supabase_history: list[MessageHistory] = [],
) -> Dict[str, Any]:
    """Process routing decision with conversation context from both sources"""
    logger.info(f"Processing decision: {decision} for message: {message}")

    # Combine histories for context
    context_parts = []

    if supabase_history:
        supabase_context = format_supabase_history(supabase_history)
        context_parts.append(f"Recent conversation:\n{supabase_context}")

    if zep_history:
        zep_context = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in zep_history]
        )
        context_parts.append(f"Long-term memory:\n{zep_context}")

    combined_context = "\n\n".join(context_parts)

    if decision == "discovery":
        topics = await extract_topics(message, zep_history)
        logger.info(f"Extracted topics: {topics}")

        if topics == ["INSUFFICIENT_CONTEXT"]:
            response = llm.complete(
                INSUFFICIENT_TEMPLATES["discovery"].format(
                    context=combined_context, message=message
                )
            )
            processed_response = await process_llm_response(message, response.text)
            return {"response": processed_response}

        crew_result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
        processed_response = await process_llm_response(message, str(crew_result))
        return {"response": processed_response}

    elif decision == "proposal":
        community_project, grant_call = await extract_proposal_details(
            message, zep_history
        )
        logger.info(f"Project: {community_project}, Grant: {grant_call}")

        if community_project == "unknown" or grant_call == "unknown":
            response = llm.complete(
                INSUFFICIENT_TEMPLATES["proposal"].format(
                    context=combined_context, message=message
                )
            )
            processed_response = await process_llm_response(message, response.text)
            return {"response": processed_response}

        crew_result = (
            ProposalWriterCrew()
            .crew()
            .kickoff(inputs={"project": community_project, "grant": grant_call})
        )
        processed_response = await process_llm_response(message, str(crew_result))
        return {"response": processed_response}

    elif decision == "heartbeat":
        processed_response = await process_llm_response(
            message, str({"is_alive": True})
        )
        return {"response": processed_response}

    elif decision == "onboarding":
        result = OnboardingCrew().crew().kickoff()
        processed_response = await process_llm_response(message, str(result))
        logger.info(f"Processed onboarding response: {processed_response}")
        return {"response": processed_response}

    else:
        return {"error": f"Unknown decision type: {decision}"}


def format_supabase_history(history: list[MessageHistory]) -> str:
    """Format last 10 Supabase messages into conversation format"""
    if not history:
        return ""

    # Get last 10 messages
    limited_history = history[-10:]

    formatted = []
    for msg in limited_history:
        formatted.extend([f"human: {msg.human}", f"assistant: {msg.ai}"])

    return "\n".join(formatted[-10:])  # Take last 10 messages total


@router.post("/classify", response_model=ClassifierResponse)
async def classifier_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
    message_history: Optional[str] = Form(default=None),  # JSON string
) -> ClassifierResponse:
    """Main route handler with conversation memory"""
    try:
        # Generate a default session_id if none provided
        current_session_id = session_id or str(uuid.uuid4())
        user_id = f"{current_session_id}_{uuid.uuid4().hex}"

        logger.info(f"New request - Session: {current_session_id}, User: {user_id}")

        # Initialize both history sources
        zep = ZepConversationManager()
        zep_session_id = await zep.get_or_create_session(
            user_id=user_id, session_id=current_session_id
        )

        # Process inputs
        combined_parts = []

        if audio is not None:
            transcription = await process_audio_file(audio)
            logger.info(f"Audio transcription: {transcription}")
            combined_parts.append(f'Transcription: "{transcription}"')

        if message:
            logger.info(f"Text message: {message}")
            combined_parts.append(f'Message: "{message}"')

        combined_message = "\n".join(combined_parts)
        if not combined_message:
            return ClassifierResponse(result="Error: No valid input provided")

        # Get both conversation histories
        zep_history = await zep.get_conversation_history(zep_session_id)
        supabase_history = []
        if message_history:
            try:
                supabase_history = [
                    MessageHistory(**msg) for msg in json.loads(message_history)
                ]
            except json.JSONDecodeError:
                logger.warning("Invalid message_history JSON format")

        # Combine both histories for context
        zep_context = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in zep_history]
        )
        supabase_context = format_supabase_history(supabase_history)

        combined_context = f"""Recent conversation:\n{supabase_context}\n\nLong-term memory:\n{zep_context}"""

        logger.info(f"Combined context:\n{combined_context}")

        # Use combined context in router prompt
        router_prompt = PromptTemplate(
            """Previous conversation:\n{context}\n\n"""
            """Given the current user message, determine the appropriate service:"""
            """\n{message}\n\n"""
            """Return only one word (discovery/proposal/onboarding/heartbeat):"""
        )

        response = llm.complete(
            router_prompt.format(context=combined_context, message=combined_message)
        )
        decision = response.text.strip().lower()

        # Process decision using combined context
        result = await process_decision(
            decision, combined_message, zep_history, supabase_history
        )

        # Process final result if it's not already processed
        if isinstance(result.get("response"), str):
            final_result = await process_llm_response(combined_message, str(result))
        else:
            final_result = str(result)

        # Truncate if result exceeds character limit
        if len(final_result) > 2499:
            logger.warning(
                f"Result exceeded 2499 characters (was {len(final_result)}). Truncating..."
            )
            final_result = final_result[:2499]

        # Log both result and character count
        logger.info(f"Final result ({len(final_result)} chars): {final_result}")

        await zep.add_conversation(zep_session_id, combined_message, final_result)
        return ClassifierResponse(result=final_result, session_id=zep_session_id)

    except Exception as e:
        logger.error(f"Error in classifier route: {str(e)}")
        error_msg = await process_llm_response(combined_message, f"Error: {str(e)}")
        return ClassifierResponse(result=error_msg)
