import os

from fastapi import APIRouter
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse

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
- heartbeat: For checking system health

User message: {message}

Return only one word (discovery/proposal/heartbeat):"""

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
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
    try:
        # Get routing decision from LLM
        decision = router_chain.run(message=request.message).strip().lower()

        # Print input message and decision for debugging
        print("\n==================================================")
        print(f"           INPUT MESSAGE: {request.message}")
        print("==================================================")
        print(f"               DECISION: {decision}")
        print("==================================================\n")

        # Handle different decision paths
        if decision == "discovery":
            # Extract topics using LLM (limited to 5 in prompt)
            topics_raw = topic_chain.run(message=request.message)
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
            extracted = proposal_chain.run(message=request.message).split("|")
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

        else:
            result = {"error": f"Unknown decision type: {decision}"}

    except Exception as e:
        result = {"error": f"Error processing request: {str(e)}"}

    return SupervisorResponse(result=str(result))
