from eda_ai_api.core import config


def test_grant_discovery(test_client) -> None:
    response = test_client.get(
        "/api/grant/discovery",
        headers={"token": str(config.API_KEY)}
    )
    assert response.status_code == 200
    assert response.json() == {"result": "success"}


def test_grant_discovery_no_auth(test_client) -> None:
    response = test_client.get("/api/grant/discovery")
    assert response.status_code == 400
