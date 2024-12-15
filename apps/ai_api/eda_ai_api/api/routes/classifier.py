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
from eda_ai_api.utils.prompts import (
    INSUFFICIENT_TEMPLATES,
    PROPOSAL_TEMPLATE,
    RESPONSE_PROCESSOR_TEMPLATE,
    TOPIC_TEMPLATE,
)

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


async def process_llm_response(message: str, response: str) -> str:
    processed = llm.complete(
        RESPONSE_PROCESSOR_TEMPLATE.format(original_message=message, response=response)
    )
    return processed.text


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
            processed_response = await process_llm_response(message, response.text)
            return {"response": processed_response}

        # Add return for successful discovery
        crew_result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
        processed_response = await process_llm_response(message, str(crew_result))
        return {"response": processed_response}

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
            processed_response = await process_llm_response(message, response.text)
            return {"response": processed_response}

        # Add crew result and return
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


@router.post("/classify", response_model=ClassifierResponse)
async def classifier_route(
    message: Optional[str] = Form(default=None),
    audio: Optional[UploadFile] = File(default=None),
    session_id: Optional[str] = Form(default=None),
) -> ClassifierResponse:
    """Main route handler with conversation memory"""
    try:
        # Generate a default session_id if none provided
        current_session_id = session_id or str(uuid.uuid4())
        user_id = f"{current_session_id}_{uuid.uuid4().hex}"

        logger.info(f"New request - Session: {current_session_id}, User: {user_id}")

        zep = ZepConversationManager()
        session_id = await zep.get_or_create_session(
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

        # Get conversation history and make decision
        history = await zep.get_conversation_history(session_id)
        context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])

        router_prompt = PromptTemplate(
            """Previous conversation:\n{context}\n\n"""
            """Given the current user message, determine the appropriate service:"""
            """\n{message}\n\n"""
            """Return only one word (discovery/proposal/onboarding/heartbeat):"""
        )

        response = llm.complete(
            router_prompt.format(context=context, message=combined_message)
        )
        decision = response.text.strip().lower()

        # Process decision and store conversation
        result = await process_decision(decision, combined_message, history)

        # Process final result if it's not already processed
        if isinstance(result.get("response"), str):
            final_result = await process_llm_response(combined_message, str(result))
        else:
            final_result = str(result)

        await zep.add_conversation(session_id, combined_message, final_result)
        return ClassifierResponse(result=final_result, session_id=session_id)

    except Exception as e:
        logger.error(f"Error in classifier route: {str(e)}")
        error_msg = await process_llm_response(combined_message, f"Error: {str(e)}")
        return ClassifierResponse(result=error_msg)
