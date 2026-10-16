import requests
from state import MainAgentState

def skill_allocator(state: MainAgentState) -> MainAgentState:
    print("--- SKILL ALLOCATOR: Finding candidate skills from DataPool ---")
    
    if state.get("action") != "Skill":
        return state

    keywords = state.get("keywords", [])
    profile = state.get("profile", {})
    existing_skills = set(profile.get("skills", []))
    
    try:
        response = requests.post(
            "https://your-backend-api.com/api/datapool/skills/allocate",
            json={
                "keywords": keywords,
                "excluded_skill_ids": list(existing_skills),
                "limit": 5  # Requesting top 5 matches
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            # Returns the top matching skill IDs and details for the filter/best match pipeline[cite: 2, 9]
            return {
                "skill_ids": data.get("skill_ids", [])[:5],
            }
            
    except Exception as e:
        print(f"Error communicating with DataPool skill allocation API: {e}")
        
    return {"skill_ids": []}