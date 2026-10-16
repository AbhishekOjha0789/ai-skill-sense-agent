import os
import requests
from state import MainAgentState

# Define base backend URL from environment with a fallback default
BACKEND_API_URL = os.environ.get(
    "BACKEND_API_URL", "https://your-backend-api.com"
)

def quest_allocator(state: MainAgentState) -> MainAgentState:
    print("--- QUEST ALLOCATOR: Finding candidate quests from DataPool ---")
    
    if state.get("action") != "Quest":
        return state

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
            timeout=40,
        )
        
        if response.status_code == 200:
            data = response.json()
            # Returns the top 5 matching quest IDs and details[cite: 2, 9]
            return {
                "quest_ids": data.get("quest_ids", [])[:5],
            }
            
    except Exception as e:
        print(f"Error communicating with DataPool quest allocation API: {e}")
        
    return {"quest_ids": []}