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

from eda_ai_api.models.classifier import ClassifierResponse
from eda_ai_api.utils.audio_utils import process_audio_file
from eda_ai_api.utils.memory import ZepConversationManager
from eda_ai_api.utils.prompts import (INSUFFICIENT_TEMPLATES,
                                      PROPOSAL_TEMPLATE, ROUTER_TEMPLATE,
                                      TOPIC_TEMPLATE)

router = APIRouter()

# Setup LLM
llm = Groq(
    model="llama3-groq-70b-8192-tool-use-preview",
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


async def process_decision(
    decision: str, message: str, history: list
) -> Dict[str, Any]:
    """Process routing decision with conversation context"""
    logger.info(f"Processing decision: {decision} for message: {message}")

    if decision == "discovery":
        topics = await extract_topics(message, history)
        logger.info(f"Extracted topics: {topics}")

        if topics == ["INSUFFICIENT_CONTEXT"]:
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            response = llm.complete(
                INSUFFICIENT_TEMPLATES["discovery"].format(
                    context=context, message=message
                )
            )
            return {"response": response.text}

    elif decision == "proposal":
        community_project, grant_call = await extract_proposal_details(message, history)
        logger.info(f"Project: {community_project}, Grant: {grant_call}")

        if community_project == "unknown" or grant_call == "unknown":
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            response = llm.complete(
                INSUFFICIENT_TEMPLATES["proposal"].format(
                    context=context, message=message
                )
            )
            return {"response": response.text}

    elif decision == "heartbeat":
        return {"is_alive": True}

    elif decision == "onboarding":
        return OnboardingCrew().crew().kickoff()

    else:
        return {"error": f"Unknown decision type: {decision}"}


@router.post("/classify", response_model=ClassifierResponse)
async def classifier_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
) -> ClassifierResponse:
    """Main route handler with conversation memory"""
    try:
        logger.info(
            f"New request - Session: {session_id}, User: {session_id + uuid.uuid4().hex}"
        )

        zep = ZepConversationManager()
        session_id = await zep.get_or_create_session(
            user_id=session_id + uuid.uuid4().hex, session_id=session_id
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

        # Get conversation history and make decision
        history = await zep.get_conversation_history(session_id)
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

        router_prompt = PromptTemplate(
            """Previous conversation:\n{context}\n\nGiven the current user message, determine the appropriate service:\n{message}\n\nReturn only one word (discovery/proposal/onboarding/heartbeat):"""
        )

        response = llm.complete(
            router_prompt.format(context=context, message=combined_message)
        )
        decision = response.text.strip().lower()

        # Process decision and store conversation
        result = await process_decision(decision, combined_message, history)
        await zep.add_conversation(session_id, combined_message, str(result))

        return ClassifierResponse(result=str(result), session_id=session_id)

    except Exception as e:
        logger.error(f"Error in classifier route: {str(e)}")
        return ClassifierResponse(result=f"Error: {str(e)}")
