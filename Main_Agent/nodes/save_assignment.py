import os

import requests

from .activity_logger import post_activity_log
from ..state import MainAgentState


def save_assignment(state: MainAgentState) -> MainAgentState:
    user_id = state.get("user_id")
    assignment_type = state.get("action")
    item_id = state.get("best_match")

    if not user_id or assignment_type not in {"Skill", "Quest"} or not item_id:
        raise ValueError("A user, selected skill or quest, and its ID are required.")

    backend_url = os.environ.get("BACKEND_API_URL")
    agent_secret = os.environ.get("AGENT_SECRET_KEY")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not agent_secret:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")

    response = requests.post(
        f"{backend_url.rstrip('/')}/api/users/{user_id}/assignments",
        json={"assignment_type": assignment_type, "item_id": item_id},
        headers={"X-Agent-Secret": agent_secret},
        timeout=40,
    )
    response.raise_for_status()
    result = response.json()

    assignment_name = "skill" if assignment_type == "Skill" else "quest"
    post_activity_log(
        user_id=user_id,
        activity_type=f"{assignment_name}_assignment",
        log_desc=f"Assigned {assignment_name} {item_id}.",
        event_id=f"assignment:{assignment_name}:{item_id}",
    )

    return {
        "assignment_status": result["status"],
    }
