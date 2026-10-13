# nodes/datapool.py
import os
import json
import requests
from state import AgentState

def datapool(state: AgentState) -> AgentState:
    print("--- DATAPOOL: Persisting skill data into the database ---")
    
    content_str = state.get("content", "{}")
    is_duplicate = state.get("duplicate")
    matching_skill_id = state.get("matching_skill_id")
    
    backend_url = os.environ.get("BACKEND_API_URL", "https://your-backend-api.com")
    
    try:
        skill_data = json.loads(content_str)
        
        if is_duplicate == "Yes" and matching_skill_id:
            # Update existing skill entry via backend
            endpoint = f"{backend_url}/api/skills/{matching_skill_id}"
            print(f"Updating existing skill ID: {matching_skill_id}")
            
            response = requests.put(endpoint, json=skill_data, timeout=10)
            if response.status_code == 200:
                print("Successfully updated existing skill in database.")
            else:
                print(f"Failed to update skill. Status code: {response.status_code}")
                
        else:
            # Insert brand new skill entry via backend
            endpoint = f"{backend_url}/api/skills/create"
            print("Inserting new skill entry into database.")
            
            response = requests.post(endpoint, json=skill_data, timeout=10)
            if response.status_code in [200, 201]:
                print("Successfully inserted new skill into database.")
            else:
                print(f"Failed to insert skill. Status code: {response.status_code}")
                
    except Exception as e:
        print(f"Error communicating with backend database in Datapool node: {e}")
        
    return state