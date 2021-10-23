from fastapi.testclient import TestClient

user_name = "TestUser"
password = "test"


def test_register(client: TestClient):
    register_data = {"user_name": user_name, "password": password}

    # does creating a user work
    r = client.post("/auth/registration", data=register_data)
    r_json = r.json()
    assert r.status_code == 200
    assert "user_name" in r_json
    assert r_json["user_name"] == user_name

    # does creating a user work with the same args
    r = client.post("/auth/registration", data=register_data)
    assert r.status_code == 400


def test_get_access_token(client: TestClient):
    login_data = {
        "username": user_name,
        "password": password,
    }

    # do we get a token
    r = client.post("/auth/token", data=login_data)
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
