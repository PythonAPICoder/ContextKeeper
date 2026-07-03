from fastapi.testclient import TestClient

from ctxkeeper.app import create_app
from ctxkeeper.config import Settings


def test_health_endpoint() -> None:
    app = create_app(Settings())
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
