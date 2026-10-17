import os
import requests
from ..state import MainAgentState

# Define base backend URL from environment with a fallback default
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")

AGENT_SECRET_KEY = os.environ.get("AGENT_SECRET_KEY")

def quest_allocator(state: MainAgentState) -> MainAgentState:
    print("--- QUEST ALLOCATOR: Finding candidate quests from DataPool ---")
    
    if state.get("action") != "Quest":
        return state

    if not AGENT_SECRET_KEY:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
    if not BACKEND_API_URL:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")

    keywords = state.get("keywords", [])
    profile = state.get("profile", {})
    
    excluded_quests = set(
        profile.get("active_quests", []) +
        profile.get("completed_quest", []) +
        profile.get("failed_quests", [])
    )
    
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/datapool/quests/allocate",
            json={
                "keywords": keywords,
                "excluded_quest_ids": list(excluded_quests),
                "limit": 5,  # Requesting top 5 matches
            },
            headers={"X-Agent-Secret": AGENT_SECRET_KEY},
            timeout=40,
        )
        
        response.raise_for_status()
        data = response.json()
        return {"quest_ids": data.get("quest_ids", [])[:5]}
    except requests.RequestException as exc:
        raise RuntimeError("Quest allocation request to backend failed.") from exc