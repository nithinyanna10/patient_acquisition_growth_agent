def get_token(client):
    response = client.post(
        "/v1/auth/token",
        data={"username": "admin@example.com", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_login_and_me(client):
    token = get_token(client)
    me = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "admin@example.com"


def test_workstream_upsert(client):
    token = get_token(client)
    payload = {
        "id": "ws-1",
        "name": "EHR Integration",
        "owner": "Marcus",
        "status": "On Track",
        "progress": 80,
        "priority": "High",
        "blocker": None,
    }
    response = client.put(
        "/v1/workstreams/ws-1",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "On Track"
