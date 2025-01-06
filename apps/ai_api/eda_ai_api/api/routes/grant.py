from fastapi import APIRouter
from opportunity_finder.crew import OpportunityFinderCrew
from proposal_writer.crew import ProposalWriterCrew

from eda_ai_api.models.grant_discovery import GrantDiscoveryResult
from eda_ai_api.models.grant_proposal import ProposalWritingResult

router = APIRouter()


@router.post("/discovery", response_model=GrantDiscoveryResult, name="discovery")
async def discover_grants(topics: list[str]) -> GrantDiscoveryResult:
    result = GrantDiscoveryResult(result="success")
    topics_str = ", ".join(topics)
    crew_result = OpportunityFinderCrew().crew().kickoff(inputs={"topics": topics_str})
    # process = run()
    print(crew_result)
    return result


@router.post("/proposal", response_model=ProposalWritingResult, name="proposal")
async def write_proposal(project: str, grant: str) -> ProposalWritingResult:
    crew_result = (
        ProposalWriterCrew().crew().kickoff(inputs={"project": project, "grant": grant})
    )
    return ProposalWritingResult(result=str(crew_result))
