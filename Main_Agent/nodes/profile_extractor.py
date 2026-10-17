import os
import requests
from ..state import MainAgentState

# Define base backend URL from environment with a fallback default
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")

AGENT_SECRET_KEY = os.environ.get("AGENT_SECRET_KEY")

def profile_extractor(state: MainAgentState) -> MainAgentState:
    print("--- PROFILE EXTRACTOR: Fetching comprehensive user profile ---")
    user_id = state.get("user_id")
    
    if not user_id:
        raise ValueError("No user_id found in Main Agent state.")

    if not BACKEND_API_URL:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not AGENT_SECRET_KEY:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")

    response = requests.get(
        f"{BACKEND_API_URL.rstrip('/')}/api/users/{user_id}/profile",
        headers={"X-Agent-Secret": AGENT_SECRET_KEY},
        timeout=30,
    )
    response.raise_for_status()
    profile_data = response.json()

    return {
        "profile": {
            "user_id": profile_data.get("user_id"),
            "username": profile_data.get("username"),
            "email": profile_data.get("email"),
            "age": profile_data.get("age"),
            "gender": profile_data.get("gender"),
            "interests": profile_data.get("interests", []),
            "skills": profile_data.get("skills", []),
            "active_quests": profile_data.get("active_quests", []),
            "completed_quest": profile_data.get("completed_quest", []),
            "failed_quests": profile_data.get("failed_quests", []),
            "summary": profile_data.get("summary", ""),
            "occupation": profile_data.get("occupation"),
            "experience": profile_data.get("experience"),
            "education_status": profile_data.get("education_status"),
            "education_summary": profile_data.get("education_summary"),
        }
    }