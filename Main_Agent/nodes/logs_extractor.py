import os
import requests
from ..state import MainAgentState

# Define base backend URL from environment with a fallback default
BACKEND_API_URL = os.environ.get("BACKEND_API_URL")

AGENT_SECRET_KEY = os.environ.get("AGENT_SECRET_KEY")

def logs_extractor(state: MainAgentState) -> MainAgentState:
    print("--- LOGS EXTRACTOR: Fetching latest 25 user logs ---")
    user_id = state.get("user_id")
    
    if not user_id:
        raise ValueError("No user_id found in Main Agent state.")

    if not BACKEND_API_URL:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not AGENT_SECRET_KEY:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")

    response = requests.get(
        f"{BACKEND_API_URL.rstrip('/')}/api/users/{user_id}/logs",
        params={"limit": 25},
        headers={"X-Agent-Secret": AGENT_SECRET_KEY},
        timeout=30,
    )
    response.raise_for_status()
    logs_data = response.json()

    return {
        "logs": [
            {
                "user_id": log.get("user_id"),
                "log_id": log.get("log_id"),
                "log_desc": log.get("log_desc"),
                "action_required": log.get("action_required"),
                "timestamp": log.get("timestamp"),
            }
            for log in logs_data.get("logs", [])
        ]
    }