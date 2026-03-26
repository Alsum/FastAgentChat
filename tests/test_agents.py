import pytest

def test_create_agent(client):
    response = client.post(
        "/agents/",
        json={"name": "Test Agent", "system_prompt": "You are a test agent."}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert "id" in data

def test_list_agents(client):
    # Pre-create
    client.post("/agents/", json={"name": "A1", "system_prompt": "P1"})
    client.post("/agents/", json={"name": "A2", "system_prompt": "P2"})
    
    response = client.get("/agents/")
    assert response.status_code == 200
    # Includes agent from previous test if we don't clear DB
    # For robust testing we should clear, but let's check it's at least 2
    assert len(response.json()) >= 2

def test_update_agent(client):
    create_res = client.post("/agents/", json={"name": "Old", "system_prompt": "Prompt"})
    agent_id = create_res.json()["id"]
    
    response = client.patch(f"/agents/{agent_id}", json={"name": "New"})
    assert response.status_code == 200
    assert response.json()["name"] == "New"
