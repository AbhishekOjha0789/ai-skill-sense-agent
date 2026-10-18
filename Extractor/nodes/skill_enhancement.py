# nodes/skill_enhancement.py
import os
import json
import requests
from gradio_client import Client
from ..state import AgentState
from gradio_response import parse_gradio_json

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
    result = client.predict(
        json.dumps(cluster_payload),
        api_name="/run_enhancement",
    )
    parsed_result = parse_gradio_json(result, "/run_enhancement")
    required_fields = {
        "skill_id",
        "skill_type",
        "skill_title",
        "skill_intro",
        "skill_holder_id",
        "related_quest_id",
    }
    missing_fields = required_fields.difference(parsed_result)
    if missing_fields:
        raise RuntimeError(
            "Gradio endpoint /run_enhancement response is missing fields: "
            + ", ".join(sorted(missing_fields))
        )
    if parsed_result["skill_type"] not in {
        "Technical",
        "Fitness",
        "Finance",
        "Communication",
    }:
        raise RuntimeError(
            "Gradio endpoint /run_enhancement returned an invalid skill_type."
        )
    for field in ("skill_id", "skill_title", "skill_intro"):
        if not isinstance(parsed_result[field], str) or not parsed_result[field].strip():
            raise RuntimeError(
                f"Gradio endpoint /run_enhancement field '{field}' "
                "must be a non-empty string."
            )
    for field in ("skill_holder_id", "related_quest_id"):
        value = parsed_result[field]
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise RuntimeError(
                f"Gradio endpoint /run_enhancement field '{field}' "
                "must be a list of strings."
            )
    result_str = json.dumps(parsed_result)

    return {
        "content": result_str,
        "content_id": matching_skill_id,
    }