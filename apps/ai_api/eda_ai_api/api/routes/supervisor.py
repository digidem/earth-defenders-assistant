from fastapi import APIRouter
from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from supervisor.crew import SupervisorCrew
from opportunity_finder.crew import OpportunityFinderCrew

router = APIRouter()


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
    decision = (
        SupervisorCrew().create_crew().kickoff(inputs={"message": request.message})
    )

    # Print input message
    print("\n==================================================")
    print(f"           INPUT MESSAGE: { request.message}       ")
    print("==================================================")

    # Print supervisor decision
    print("\n==================================================")
    print(f"               DECISION: {decision}                 ")
    print("==================================================\n")

    if decision.lower() == "discovery":
        topics = ["AI", "Technology"]  # Extract topics from message
        result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
    else:
        result = {"is_alive": True}

    return SupervisorResponse(result=str(result))
