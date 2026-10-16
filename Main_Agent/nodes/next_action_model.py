import json
import os
from gradio_client import Client
from state import MainAgentState

def next_action_model(state: MainAgentState) -> MainAgentState:
    print("--- NEXT ACTION MODEL: Calling Gradio client API on Hugging Face ---")
    
    # Gather required context from state
    user_profile = state.get("profile", {})
    user_logs = state.get("logs", [])
    
    # Fetch available pool identifiers from backend or state (mocked or pre-fetched if stored in state)
    # Falling back to empty or state-provided identifiers
    available_pool_identifiers = state.get("available_pool_identifiers", {
        "skill_ids": user_profile.get("skills", []),
        "quest_ids": user_profile.get("active_quests", [])
    })

    # Construct the input context JSON matching your training dataset structure
    input_context = {
        "user_profile": user_profile,
        "user_logs": user_logs,
        "available_pool_identifiers": available_pool_identifiers
    }

    input_text = json.dumps(input_context)
    hf_token = os.environ.get("HF_TOKEN")
    
    # Default fallback values
    action_result = "None"
    skills_result = []
    quests_result = []
    keywords_result = []

    try:
        # Initialize the Gradio client for your space
        client = Client("AO0789/ai-skill-sense-engine", hf_token=hf_token)
        
        # Call the specific endpoint matching your Gradio space definition
        result_str = client.predict(
            text=input_text,
            api_name="/run_next_action",
        )
        
        # Parse the JSON string response matching your model output format
        # e.g., {"user_id": "...", "skills": [...], "quests": [...], "action": "...", "keywords": [...]}
        if result_str:
            parsed_result = json.loads(result_str)
            action_result = parsed_result.get("action", "None")
            skills_result = parsed_result.get("skills", [])
            quests_result = parsed_result.get("quests", [])
            keywords_result = parsed_result.get("keywords", [])
            print("Successfully determined next action via Gradio API.")
            
    except Exception as e:
        print(f"Error communicating with Gradio Next Action client: {e}")
        
    return {
        "action": action_result,
        "skill_ids": skills_result,
        "quest_ids": quests_result,
        "keywords": keywords_result
    }