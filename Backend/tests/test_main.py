from fastapi.testclient import TestClient

from Backend.main import app

client = TestClient(app)
client.headers["Content-Type"] = "application/json"


def test_read_main():
    response = client.get("/?token=possible-super-secret-query-token", headers={"x-token": "possible-super-secret-header-token"}) #
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Bigger Applications!"}


def test_read_main_no_header():
    response = client.get("/?token=possible-super-secret-query-token") #
    assert response.status_code == 200
    assert response.json() == {"message": "Hello Bigger Applications!"}


def test_read_main_no_query():
    response = client.get("/", headers={"x-token": "possible-super-secret-header-token"}) #
    assert response.status_code == 422


def test_read_items():
    response = client.get("/items/thors_hammer?token=possible-super-secret-query-token", headers={"x-token": "possible-super-secret-header-token"}) #
    assert response.status_code == 404


def test_read_gun():
    response = client.get("/items/gun?token=possible-super-secret-query-token", headers={"x-token": "possible-super-secret-header-token"}) #
    assert response.status_code == 200
    assert response.json() == {"name": "Portal Gun", "item_id": "gun"}
