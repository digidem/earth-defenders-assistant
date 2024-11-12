from fastapi import APIRouter
from eda_ai_api.models.supervisor import SupervisorRequest, SupervisorResponse
from opportunity_finder.crew import OpportunityFinderCrew
from plugins.supervisor.crew import SupervisorCrew

router = APIRouter()


@router.post("/supervisor", response_model=SupervisorResponse)
async def supervisor_route(request: SupervisorRequest) -> SupervisorResponse:
    decision = SupervisorCrew().crew().kickoff(inputs={"message": request.message})

    if decision.lower() == "discovery":
        topics = ["AI", "Technology"]  # Extract topics from message
        result = (
            OpportunityFinderCrew().crew().kickoff(inputs={"topics": ", ".join(topics)})
        )
    else:
        result = {"is_alive": True}

    return SupervisorResponse(result=str(result))
