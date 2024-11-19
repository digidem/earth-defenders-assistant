import os
from fastapi import APIRouter
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

router = APIRouter()

print("API KEY:", os.environ.get("GROQ_API_KEY"))
# Setup LLM and prompt
llm = ChatGroq(
    model_name="llama3-groq-70b-8192-tool-use-preview",
    api_key=os.environ.get("GROQ_API_KEY"),
    temperature=0.5,
)


ROUTER_TEMPLATE = """Given a user message, determine the appropriate service to handle the request.
Choose between:
- discovery: For finding grant opportunities
- proposal: For writing grant proposals
- heartbeat: For checking system health

User message: {message}

Return only one word (discovery/proposal/heartbeat):"""

router_prompt = PromptTemplate(input_variables=["message"], template=ROUTER_TEMPLATE)

router_chain = LLMChain(llm=llm, prompt=router_prompt)


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
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
        topics = ["AI", "Technology"]
        result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
    elif decision == "proposal":
        community_project = "sample_project"
        grant_call = "sample_grant"
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

    return SupervisorResponse(result=str(result))
