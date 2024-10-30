import pytest

from eda_ai_api.core import config
from eda_ai_api.models.grant_discovery import GrantDiscoveryResult


def test_prediction(test_client) -> None:
    result = GrantDiscoveryResult.model_validate(
        {
            "result": "success",
        }
    )

    assert isinstance(result, GrantDiscoveryResult)
