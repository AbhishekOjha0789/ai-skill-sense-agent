# nodes/skill_enhancement.py
import os
import json
import requests
from gradio_client import Client
from state import AgentState

def skill_enhancement(state: AgentState) -> AgentState:
    print("--- SKILL ENHANCEMENT: Merging duplicate skills via Hugging Face Client ---")

    hf_token = os.environ.get("HF_TOKEN")
    
    new_skill_content = state.get("content", "{}")
    matching_skill_id = state.get("matching_skill_id")
    
    try:
        # 1. Fetch the existing matching skill details from your backend API
        backend_url = os.environ.get("BACKEND_API_URL", "https://your-backend-api.com")
        endpoint = f"{backend_url}/api/skills/{matching_skill_id}"
        
        response = requests.get(endpoint, timeout=10)
        existing_skill_data = {}
        if response.status_code == 200:
            existing_skill_data = response.json()
            
        # 2. Combine both skill payloads into a cluster format for the enhancer model
        cluster_payload = {
            "existing_skill": existing_skill_data,
            "new_skill_candidate": json.loads(new_skill_content)
        }
        
        # 3. Call your Gradio enhancement endpoint
        client = Client("AO0789/ai-skill-sense-engine", hf_token=hf_token)
        result_str = client.predict(
            text=json.dumps(cluster_payload),
            api_name="/run_enhancement",
        )
        
        if result_str:
            print("Successfully enhanced and unified skill profile.")
            return {
                "content": result_str,  # Updates content with the unified skill profile JSON
                "content_id": matching_skill_id # Keeps the existing skill's ID for updating
            }
            
    except Exception as e:
        print(f"Error during skill enhancement: {e}")
        
    return state