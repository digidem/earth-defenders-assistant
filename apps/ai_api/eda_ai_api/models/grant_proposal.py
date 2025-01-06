from pydantic import BaseModel


class ProposalWritingResult(BaseModel):
    result: str
