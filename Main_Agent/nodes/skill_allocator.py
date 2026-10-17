import os
import requests
from ..state import MainAgentState

# Define base backend URL from environment with a fallback default
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")

AGENT_SECRET_KEY = os.environ.get("AGENT_SECRET_KEY")

def skill_allocator(state: MainAgentState) -> MainAgentState:
    print("--- SKILL ALLOCATOR: Finding candidate skills from DataPool ---")
    
    if state.get("action") != "Skill":
        return state

    if not AGENT_SECRET_KEY:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
    if not BACKEND_API_URL:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")

    keywords = state.get("keywords", [])
    profile = state.get("profile", {})
    existing_skills = set(profile.get("skills", []))
    
    try:
        response = requests.post(
            f"{BACKEND_API_URL}/api/datapool/skills/allocate",
            json={
                "keywords": keywords,
                "excluded_skill_ids": list(existing_skills),
                "limit": 5,  # Requesting top 5 matches
            },
            headers={"X-Agent-Secret": AGENT_SECRET_KEY},
            timeout=40,
        )
        
        response.raise_for_status()
        data = response.json()
        return {"skill_ids": data.get("skill_ids", [])[:5]}
    except requests.RequestException as exc:
        raise RuntimeError("Skill allocation request to backend failed.") from exc