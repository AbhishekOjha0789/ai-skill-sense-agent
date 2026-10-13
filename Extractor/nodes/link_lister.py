# nodes/link_lister.py
import requests
from state import AgentState

def link_lister(state: AgentState) -> AgentState:
    print("--- LINK LISTER: Checking URL in database ---")
    target_url = state.get("url")
    
    try:
        # Send the URL string to your FastAPI backend endpoint
        response = requests.post(
            "https://your-backend-api.com/api/urls/process",
            json={"url": target_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            found_existing = (target_url ==  data.get("url"))
            
            if found_existing:
                return {
                    "is_visited": "Yes"
                }
            else:
                return {
                    "is_visited": "No"
                }
                
    except Exception as e:
        print(f"Error communicating with backend API: {e}")
        
    return {"is_visited": "Yes"}  # Default to "Yes" if there's an error or no response