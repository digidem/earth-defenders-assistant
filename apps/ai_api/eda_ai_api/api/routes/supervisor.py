from fastapi import APIRouter
from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from supervisor.crew import SupervisorCrew
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

router = APIRouter()


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
    # Get crew decision
    crew_response = (
        SupervisorCrew().create_crew().kickoff(inputs={"message": request.message})
    )

    # Extract decision from crew response
    decision = str(crew_response).lower()

    # Print input message and decision for debugging
    print("\n==================================================")
    print(f"           INPUT MESSAGE: {request.message}")
    print("==================================================")
    print(f"               DECISION: {decision}")
    print("==================================================\n")

    # Handle different decision paths
    if decision == "discovery":
        # TODO: Extract topics from the actual message
        topics = ["AI", "Technology"]
        result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
    elif decision == "proposal":
        # Initialize ProposalWriterCrew with context from the message
        # TODO: Extract project and grant details from message
        community_project = "sample_project"  # This should come from message parsing
        grant_call = "sample_grant"  # This should come from message parsing
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
