def get_token(client):
    response = client.post(
        "/v1/auth/token",
        data={"username": "admin@example.com", "password": "admin123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_brief_and_simulation(client):
    token = get_token(client)
    brief = client.get("/v1/agent/brief", headers={"Authorization": f"Bearer {token}"})
    assert brief.status_code == 200
    assert "readiness" in brief.json()

    sim = client.post(
        "/v1/agent/simulate",
        json={
            "resolve_raid_ids": ["risk-1"],
            "pass_checklist_ids": [],
            "recover_milestone_ids": ["ms-1"],
            "recover_workstream_ids": ["ws-1"],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert sim.status_code == 200
    assert "projected_score" in sim.json()


def test_plan_generation(client):
    token = get_token(client)
    plan = client.post(
        "/v1/agent/plan",
        json={"objective": "Reach GO by week 8", "horizon_days": 14},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert plan.status_code == 200
    assert len(plan.json()["steps"]) >= 1
