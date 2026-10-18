# nodes/cleaning_model.py
import os
from gradio_client import Client
from ..state import AgentState
from gradio_response import parse_gradio_json

def cleaning_model(state: AgentState) -> AgentState:
    print("--- CLEANING MODEL: Calling Gradio client API on Hugging Face ---")
    raw_content = state.get("content", "")

    hf_token = os.environ.get("HF_TOKEN")
    
    client = Client("AO0789/ai-skill-sense-engine", token=hf_token)
    result = client.predict(raw_content, api_name="/run_cleaning")
    parsed_result = parse_gradio_json(result, "/run_cleaning")
    cleaned_content = parsed_result.get("content")
    cleaned_status = parsed_result.get("cleaned")
    if not isinstance(cleaned_content, str):
        raise RuntimeError(
            "Gradio endpoint /run_cleaning response field 'content' must be a string."
        )
    if cleaned_status not in {"Yes", "No"}:
        raise RuntimeError(
            "Gradio endpoint /run_cleaning response field 'cleaned' "
            "must be 'Yes' or 'No'."
        )
    print("Successfully cleaned content via Gradio API.")
    return {
        "content": cleaned_content,
        "cleaned": cleaned_status
    }