from pydantic import BaseModel


class SupervisorResponse(BaseModel):
    result: str


class SupervisorRequest(BaseModel):
    message: str
