# nodes/skill_enhancement.py
import os
import json
import requests
from gradio_client import Client
from ..state import AgentState

def skill_enhancement(state: AgentState) -> AgentState:
    print("--- SKILL ENHANCEMENT: Merging duplicate skills via Hugging Face Client ---")

    hf_token = os.environ.get("HF_TOKEN")
    
    new_skill_content = state.get("content", "{}")
    matching_skill_id = state.get("matching_skill_id")

    if not matching_skill_id:
        raise ValueError("matching_skill_id is required for skill enhancement.")
    agent_secret = os.environ.get("AGENT_SECRET_KEY")
    backend_url = os.environ.get("BACKEND_API_URL")
    if not agent_secret:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")

    endpoint = f"{backend_url.rstrip('/')}/api/skills/{matching_skill_id}"
    response = requests.get(
        endpoint,
        headers={"X-Agent-Secret": agent_secret},
        timeout=30,
    )
    response.raise_for_status()
    existing_skill_data = response.json()

    cluster_payload = {
        "existing_skill": existing_skill_data,
        "new_skill_candidate": json.loads(new_skill_content),
    }

    client = Client("AO0789/ai-skill-sense-engine", token=hf_token)
    result_str = client.predict(
        json.dumps(cluster_payload),
        api_name="/run_enhancement",
    )
    if not result_str:
        raise RuntimeError("Skill enhancement model returned an empty result.")

    return {
        "content": result_str,
        "content_id": matching_skill_id,
    }