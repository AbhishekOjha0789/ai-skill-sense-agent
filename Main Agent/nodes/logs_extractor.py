import requests
from state import MainAgentState

def logs_extractor(state: MainAgentState) -> MainAgentState:
    print("--- LOGS EXTRACTOR: Fetching latest 25 user logs ---")
    user_id = state.get("user_id")
    
    if not user_id:
        print("Error: No user_id found in state.")
        return {"logs": []}

    try:
        # Request recent logs from your FastAPI backend with a limit of 25
        response = requests.get(
            f"https://your-backend-api.com/api/users/{user_id}/logs",
            params={"limit": 25}
        )
        
        if response.status_code == 200:
            logs_data = response.json()
            
            # Map each log based on your exact schema:
            # - user_id, log_id, log_desc, action_required ('Yes'/'No'), timestamp (ISO-8601)[cite: 8]
            formatted_logs = []
            for log in logs_data.get("logs", []):
                formatted_logs.append({
                    "user_id": log.get("user_id"),
                    "log_id": log.get("log_id"),
                    "log_desc": log.get("log_desc"),
                    "action_required": log.get("action_required"),
                    "timestamp": log.get("timestamp")
                })
                
            return {"logs": formatted_logs}
        else:
            print(f"Failed to fetch logs. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"Error communicating with backend API for log extraction: {e}")
        
    return {"logs": []}