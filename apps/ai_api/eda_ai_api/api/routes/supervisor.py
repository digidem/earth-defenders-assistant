import os

from fastapi import APIRouter, File, UploadFile, Form
from typing import Optional
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from onboarding.crew import OnboardingCrew
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from eda_ai_api.utils.audio_converter import convert_ogg
from eda_ai_api.utils.transcriber import transcribe_audio

import tempfile

router = APIRouter()

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

# Create prompt templates
router_prompt = PromptTemplate(input_variables=["message"], template=ROUTER_TEMPLATE)
topic_prompt = PromptTemplate(
    input_variables=["message"], template=TOPIC_EXTRACTOR_TEMPLATE
)
proposal_prompt = PromptTemplate(
    input_variables=["message"], template=PROPOSAL_EXTRACTOR_TEMPLATE
)

# Create LLM chains
router_chain = LLMChain(llm=llm, prompt=router_prompt)
topic_chain = LLMChain(llm=llm, prompt=topic_prompt)
proposal_chain = LLMChain(llm=llm, prompt=proposal_prompt)


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(
    message: Optional[str] = Form(None), audio: Optional[UploadFile] = File(None)
) -> SupervisorResponse:
    ALLOWED_FORMATS = {
        "audio/mpeg": "mp3",
        "audio/mp4": "mp4",
        "audio/mpeg": "mpeg",
        "audio/mpga": "mpga",
        "audio/mp4": "m4a",
        "audio/wav": "wav",
        "audio/webm": "webm",
        "audio/ogg": "ogg",
    }

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

    try:
        if audio:
            content_type = detect_content_type(audio)
            content = await audio.read()

            try:
                audio_path = ""
                # Default to mp3 if content type detection failed
                if not content_type:
                    content_type = "audio/mpeg"

                if content_type == "audio/ogg":
                    audio_path = convert_ogg(content, output_format="mp3")
                else:
                    with tempfile.NamedTemporaryFile(
                        suffix=f".{ALLOWED_FORMATS.get(content_type, 'mp3')}",
                        delete=False,
                    ) as temp_file:
                        temp_file.write(content)
                        audio_path = temp_file.name

                transcription = transcribe_audio(audio_path)
                print("\n==================================================")
                print(f"           TRANSCRIPTION: {transcription}")
                print("==================================================\n")

                if os.path.exists(audio_path):
                    os.unlink(audio_path)

                # Process transcription through the router chain
                decision = router_chain.run(message=transcription).strip().lower()

                # Continue with existing decision handling logic...
                if decision == "discovery":
                    topics_raw = topic_chain.run(message=transcription)
                    topics = [t.strip() for t in topics_raw.split(",") if t.strip()][:5]
                    if not topics:
                        topics = ["AI", "Technology"]
                    result = (
                        OpportunityFinderCrew()
                        .crew()
                        .kickoff(inputs={"topics": ", ".join(topics)})
                    )

                elif decision == "proposal":
                    extracted = proposal_chain.run(message=transcription).split("|")
                    community_project = (
                        extracted[0].strip() if len(extracted) > 0 else "unknown"
                    )
                    grant_call = (
                        extracted[1].strip() if len(extracted) > 1 else "unknown"
                    )
                    result = (
                        ProposalWriterCrew(
                            community_project=community_project, grant_call=grant_call
                        )
                        .crew()
                        .kickoff()
                    )

                elif decision == "heartbeat":
                    result = {"is_alive": True}

                elif decision == "onboarding":
                    result = OnboardingCrew().crew().kickoff()

                else:
                    result = {"error": f"Unknown decision type: {decision}"}

                return SupervisorResponse(result=str(result))

            except Exception as e:
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
                return SupervisorResponse(result=f"Error processing audio: {str(e)}")

        elif message:
            # Existing message handling logic
            decision = router_chain.run(message=message).strip().lower()

            # Print input message and decision for debugging
            print("\n==================================================")
            print(f"           INPUT MESSAGE: {message}")
            print("==================================================")
            print(f"               DECISION: {decision}")
            print("==================================================\n")

            # Handle different decision paths
            if decision == "discovery":
                # Extract topics using LLM (limited to 5 in prompt)
                topics_raw = topic_chain.run(message=message)
                topics = [t.strip() for t in topics_raw.split(",") if t.strip()][
                    :5
                ]  # Safety check
                if not topics:
                    topics = ["AI", "Technology"]  # Fallback topics

                print("==================================================")
                print(f"           EXTRACTED TOPICS: {topics}")
                print("==================================================\n")

                result = (
                    OpportunityFinderCrew()
                    .crew()
                    .kickoff(inputs={"topics": ", ".join(topics)})
                )

            elif decision == "proposal":
                # Extract project and grant details using LLM
                extracted = proposal_chain.run(message=message).split("|")
                community_project = (
                    extracted[0].strip() if len(extracted) > 0 else "unknown"
                )
                grant_call = extracted[1].strip() if len(extracted) > 1 else "unknown"

                print("==================================================")
                print(f"     PROJECT NAME: {community_project}")
                print(f"     GRANT PROGRAM: {grant_call}")
                print("==================================================\n")

                result = (
                    ProposalWriterCrew(
                        community_project=community_project, grant_call=grant_call
                    )
                    .crew()
                    .kickoff()
                )

            elif decision == "heartbeat":
                result = {"is_alive": True}

            elif decision == "onboarding":
                # Generate guide using OnboardingCrew
                result = OnboardingCrew().crew().kickoff()

            else:
                result = {"error": f"Unknown decision type: {decision}"}

        else:
            return SupervisorResponse(
                result="Error: Neither message nor audio provided"
            )

    except Exception as e:
        return SupervisorResponse(result=f"Error processing request: {str(e)}")
