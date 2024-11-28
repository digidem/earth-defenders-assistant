import os
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, UploadFile
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from onboarding.crew import OnboardingCrew
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

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

# Setup LLM and prompt
llm = ChatGroq(
    model_name="llama3-groq-70b-8192-tool-use-preview",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)

ROUTER_TEMPLATE = """
Given a user message, determine the appropriate service to handle the request.
Choose between:
- discovery: For finding grant opportunities
- proposal: For writing grant proposals
- onboarding: For getting help using the system
- heartbeat: For checking system health

User message: {message}

Return only one word (discovery/proposal/onboarding/heartbeat):"""

TOPIC_EXTRACTOR_TEMPLATE = """
Extract up to 5 most relevant topics for grant opportunity research from the user message.
Return only a comma-separated list of topics (maximum 5), no other text.

User message: {message}

Topics:"""

PROPOSAL_EXTRACTOR_TEMPLATE = """
Extract the community project name and grant program name from the user message.
Return in format: project_name|grant_name
If either cannot be determined, use "unknown" as placeholder.

User message: {message}

Output:"""

# Create prompt templates and chains
router_prompt = PromptTemplate(input_variables=["message"], template=ROUTER_TEMPLATE)
topic_prompt = PromptTemplate(
    input_variables=["message"], template=TOPIC_EXTRACTOR_TEMPLATE
)
proposal_prompt = PromptTemplate(
    input_variables=["message"], template=PROPOSAL_EXTRACTOR_TEMPLATE
)

router_chain = LLMChain(llm=llm, prompt=router_prompt)
topic_chain = LLMChain(llm=llm, prompt=topic_prompt)
proposal_chain = LLMChain(llm=llm, prompt=proposal_prompt)


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
    topics_raw = topic_chain.run(message=message)
    topics = [t.strip() for t in topics_raw.split(",") if t.strip()][:5]
    return topics if topics else ["AI", "Technology"]


def extract_proposal_details(message: str) -> tuple[str, str]:
    """Extract project and grant details"""
    extracted = proposal_chain.run(message=message).split("|")
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
        return (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
    elif decision == "proposal":
        community_project, grant_call = extract_proposal_details(message)
        print(f"     PROJECT NAME: {community_project}")
        print(f"     GRANT PROGRAM: {grant_call}")
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
        if audio:
            transcription = await process_audio(audio)
            print("==================================================\n")
            print(f"           TRANSCRIPTION: {transcription}")
            print("==================================================\n")
            decision = router_chain.run(message=transcription).strip().lower()
            result = process_decision(decision, transcription)
        elif message:
            print("==================================================\n")
            print(f"           INPUT MESSAGE: {message}")
            print("==================================================\n")
            decision = router_chain.run(message=message).strip().lower()
            result = process_decision(decision, message)
        else:
            return ClassifierResponse(
                result="Error: Neither message nor audio provided"
            )

        return ClassifierResponse(result=str(result))

    except Exception as e:
        return ClassifierResponse(result=f"Error processing request: {str(e)}")
