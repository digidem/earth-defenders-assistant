from fastapi import APIRouter
from opportunity_finder.crew import OpportunityFinderCrew

from eda_ai_api.models.grant_discovery import GrantDiscoveryResult

router = APIRouter()


@router.post("/discovery", response_model=GrantDiscoveryResult, name="discovery")
async def discover_grants(topics: list[str]) -> GrantDiscoveryResult:
    result = GrantDiscoveryResult(result="success")
    topics_str = ", ".join(topics)
    crew_result = OpportunityFinderCrew().crew().kickoff(inputs={"topics": topics_str})
    # process = run()
    print(crew_result)
    return result
