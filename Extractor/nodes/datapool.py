# nodes/datapool.py
import os
import json
import requests
from ..state import AgentState

def datapool(state: AgentState) -> AgentState:
    print("--- DATAPOOL: Persisting skill data into the database ---")
    
    content_str = state.get("content", "{}")
    is_duplicate = state.get("duplicate")
    matching_skill_id = state.get("matching_skill_id")
    
    backend_url = os.environ.get("BACKEND_API_URL")
    agent_secret = os.environ.get("AGENT_SECRET_KEY")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not agent_secret:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")

    skill_data = json.loads(content_str)
    headers = {"X-Agent-Secret": agent_secret}

    if is_duplicate == "Yes" and matching_skill_id:
        endpoint = f"{backend_url.rstrip('/')}/api/skills/{matching_skill_id}"
        print(f"Updating existing skill ID: {matching_skill_id}")
        response = requests.put(
            endpoint, json=skill_data, headers=headers, timeout=30
        )
    else:
        endpoint = f"{backend_url.rstrip('/')}/api/skills/create"
        print("Inserting new skill entry into database.")
        response = requests.post(
            endpoint, json=skill_data, headers=headers, timeout=30
        )

    response.raise_for_status()
    return state