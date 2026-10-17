# nodes/cleaning_model.py
import json
import os
from gradio_client import Client
from ..state import AgentState

def cleaning_model(state: AgentState) -> AgentState:
    print("--- CLEANING MODEL: Calling Gradio client API on Hugging Face ---")
    raw_content = state.get("content", "")

    hf_token = os.environ.get("HF_TOKEN")
    
    cleaned_content = raw_content
    cleaned_status = "No"
    
    try:
        # Initialize the Gradio client for your space
        client = Client("AO0789/ai-skill-sense-engine", hf_token=hf_token)
        
        # Call the specific cleaning endpoint
        result_str = client.predict(
            text=raw_content,
            api_name="/run_cleaning",
        )
        
        # The output is a JSON string matching your training format
        # e.g., {"content_id": "...", "content": "...", "cleaned": "Yes"}
        if result_str:
            parsed_result = json.loads(result_str)
            cleaned_content = parsed_result.get("content", raw_content)
            cleaned_status = parsed_result.get("cleaned", "No")
            print("Successfully cleaned content via Gradio API.")
            
    except Exception as e:
        print(f"Error communicating with Gradio cleaning client: {e}")
        
    return {
        "content": cleaned_content,
        "cleaned": cleaned_status
    }