# nodes/url_list.py
import requests
from state import AgentState

def url_list(state: AgentState) -> AgentState:
    print("--- URL LIST: Fetching url_id from database ---")
    target_url = state.get("url")
    
    try:
        # Request the URL record details (including url_id) from your backend
        response = requests.post(
            "https://your-backend-api.com/api/urls/get-id",
            json={"url": target_url}
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "url_id": data.get("url_id")
            }
                
    except Exception as e:
        print(f"Error fetching url_id from backend API: {e}")
        
    return state