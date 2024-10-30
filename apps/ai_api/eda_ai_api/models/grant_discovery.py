from pydantic import BaseModel


class GrantDiscoveryResult(BaseModel):
    result: str
