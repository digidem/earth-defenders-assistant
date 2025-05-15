import secrets
from typing import Optional

from eda_config import ConfigLoader
from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED

from eda_ai_api.core.messages import AUTH_REQ, NO_API_KEY

config = ConfigLoader.get_config()
api_key = APIKeyHeader(name="token", auto_error=False)


def validate_request(header: Optional[str] = Security(api_key)) -> bool:
    if header is None:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST, detail=NO_API_KEY, headers={}
        )
    if not secrets.compare_digest(
        header, str(config.api_keys.groq)
    ):  # Using GROQ API key as an example
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail=AUTH_REQ, headers={}
        )
    return True
