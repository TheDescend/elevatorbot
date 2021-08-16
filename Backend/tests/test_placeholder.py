from fastapi.testclient import TestClient

from Backend.main import app

client = TestClient(app)
client.headers["Content-Type"] = "application/json"


def test_placeholder():
    pass
