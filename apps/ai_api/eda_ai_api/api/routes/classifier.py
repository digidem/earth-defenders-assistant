import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile
from llama_index.llms.groq import Groq
from onboarding.crew import OnboardingCrew
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

from llama_index.core import PromptTemplate
from eda_ai_api.models.classifier import ClassifierResponse
from eda_ai_api.utils.audio_converter import convert_ogg
from eda_ai_api.utils.transcriber import transcribe_audio

router = APIRouter()

ALLOWED_FORMATS = {
    "audio/mpeg": "mp3",
    "audio/mp4": "mp4",
    "audio/mpga": "mpga",
    "audio/wav": "wav",
    "audio/webm": "webm",
    "audio/ogg": "ogg",
}

# Setup LLM
llm = Groq(
    model="llama3-groq-70b-8192-tool-use-preview",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)

# Define prompts
ROUTER_TEMPLATE = PromptTemplate(
    """Given a user message, determine the appropriate service to handle the request.
    Choose between:
    - discovery: For finding grant opportunities
    - proposal: For writing grant proposals
    - onboarding: For getting help using the system
    - heartbeat: For checking system health

    User message: {message}

    Return only one word (discovery/proposal/onboarding/heartbeat):"""
)

TOPIC_TEMPLATE = PromptTemplate(
    """Extract up to 5 most relevant topics for grant opportunity research from the user message.
    Return only a comma-separated list of topics (maximum 5), no other text.

    User message: {message}

    Topics:"""
)

PROPOSAL_TEMPLATE = PromptTemplate(
    """Extract the community project name and grant program name from the user message.
    Return in format: project_name|grant_name
    If either cannot be determined, use "unknown" as placeholder.

    User message: {message}

    Output:"""
)

INSUFFICIENT_PROPOSAL_TEMPLATE = PromptTemplate(
    """The user wants to write a proposal but hasn't provided enough information.
    Generate a friendly response in the same language as the user's message asking for:
    1. The project name and brief description
    2. The specific grant program they're applying to (if any)
    3. The main objectives of their project
    4. The target community or region
    
    User message: {message}
    
    Response:"""
)

INSUFFICIENT_DISCOVERY_TEMPLATE = PromptTemplate(
    """The user wants to find grant opportunities but hasn't provided enough information.
    Generate a friendly response in the same language as the user's message asking for:
    1. The main topics or areas of their project
    2. The target region or community
    3. Any specific funding requirements or preferences
    
    User message: {message}
    
    Response:"""
)


def detect_content_type(file: UploadFile) -> Optional[str]:
    """Helper to detect content type from file"""
    if hasattr(file, "content_type") and file.content_type:
        return file.content_type

    if hasattr(file, "mime_type") and file.mime_type:
        return file.mime_type

    ext = os.path.splitext(file.filename)[1].lower()
    return {
        ".mp3": "audio/mpeg",
        ".mp4": "audio/mp4",
        ".mpeg": "audio/mpeg",
        ".mpga": "audio/mpga",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".webm": "audio/webm",
        ".ogg": "audio/ogg",
    }.get(ext)


async def process_audio(audio: UploadFile) -> str:
    """Process audio file and return transcription"""
    content_type = detect_content_type(audio)
    content = await audio.read()
    audio_path = ""

    try:
        if not content_type:
            content_type = "audio/mpeg"

        if content_type == "audio/ogg":
            audio_path = convert_ogg(content, output_format="mp3")
        else:
            with tempfile.NamedTemporaryFile(
                suffix=f".{ALLOWED_FORMATS.get(content_type, 'mp3')}", delete=False
            ) as temp_file:
                temp_file.write(content)
                audio_path = temp_file.name

        return transcribe_audio(audio_path)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


def extract_topics(message: str) -> List[str]:
    """Extract topics from message"""
    response = llm.complete(TOPIC_TEMPLATE.format(message=message))
    topics = [t.strip() for t in response.text.split(",") if t.strip()][:5]
    return topics if topics else ["AI", "Technology"]


def extract_proposal_details(message: str) -> tuple[str, str]:
    """Extract project and grant details"""
    response = llm.complete(PROPOSAL_TEMPLATE.format(message=message))
    extracted = response.text.split("|")
    community_project = extracted[0].strip() if len(extracted) > 0 else "unknown"
    grant_call = extracted[1].strip() if len(extracted) > 1 else "unknown"
    return community_project, grant_call


def process_decision(decision: str, message: str) -> Dict[str, Any]:
    """Process routing decision and return result"""
    print("\n==================================================")
    print(f"               DECISION: {decision}")
    print("==================================================\n")

    if decision == "discovery":
        topics = extract_topics(message)
        print("\n==================================================")
        print(f"           EXTRACTED TOPICS: {topics}")
        print("==================================================\n")

        # If no specific topics found, ask for more information
        if topics == ["AI", "Technology"]:
            response = llm.complete(
                INSUFFICIENT_DISCOVERY_TEMPLATE.format(message=message)
            )
            return {"response": response.text}

        return (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )

    elif decision == "proposal":
        community_project, grant_call = extract_proposal_details(message)
        print(f"     PROJECT NAME: {community_project}")
        print(f"     GRANT PROGRAM: {grant_call}")

        # If either project or grant is unknown, ask for more information
        if community_project == "unknown" or grant_call == "unknown":
            response = llm.complete(
                INSUFFICIENT_PROPOSAL_TEMPLATE.format(message=message)
            )
            return {"response": response.text}

        return (
            ProposalWriterCrew(
                community_project=community_project, grant_call=grant_call
            )
            .crew()
            .kickoff()
        )

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
) -> ClassifierResponse:
    """Main route handler for classifier API"""
    try:
        combined_parts = []
        has_valid_audio = False

        # Process audio if provided
        if audio is not None:
            # Check if audio is not empty
            audio_content = await audio.read()
            has_valid_audio = len(audio_content) > 0

            if has_valid_audio:
                await audio.seek(0)
                transcription = await process_audio(audio)
                print("==================================================")
                print(f"           TRANSCRIPTION: {transcription}")
                print("==================================================")
                combined_parts.append(
                    f'Transcription of attached audio: "{transcription}"'
                )

        # Add message if provided
        if message:
            combined_parts.append(f'Message: "{message}"')

        # Combine parts with newlines
        combined_message = "\n".join(combined_parts)

        if combined_message:
            print("==================================================")
            print(f"           COMBINED MESSAGE:\n{combined_message}")
            print("==================================================")

        # Ensure we have some input to process
        if not combined_message:
            return ClassifierResponse(
                result="Error: Neither valid message nor valid audio provided"
            )

        # Process the combined input
        response = llm.complete(ROUTER_TEMPLATE.format(message=combined_message))
        decision = response.text.strip().lower()
        result = process_decision(decision, combined_message)

        return ClassifierResponse(result=str(result))

    except Exception as e:
        return ClassifierResponse(result=f"Error processing request: {str(e)}")
