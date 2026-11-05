import uuid

from fastapi.testclient import TestClient

from dicrates.main import create_app


def test_health_returns_ok_and_version() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert isinstance(body["version"], str)
    assert body["version"]


def test_db_endpoints_answer_503_without_database() -> None:
    from dicrates.core.auth import AuthenticatedUser, get_current_user
    from dicrates.core.settings import Settings

    app = create_app(Settings(_env_file=None))  # pyright: ignore[reportCallIssue]
    app.dependency_overrides[get_current_user] = lambda: AuthenticatedUser(id=uuid.uuid4())

    with TestClient(app) as client:
        response = client.get("/me")

    assert response.status_code == 503
