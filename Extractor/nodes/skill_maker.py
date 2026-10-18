# nodes/skill_maker.py
import os
import json
from google import genai
from google.genai import types
from ..state import AgentState

def skill_maker(state: AgentState) -> AgentState:
    print("--- SKILL MAKER: Generating skill candidate via Gemini 3.1 Flash Lite ---")
    cleaned_content = state.get("content", "")
    
    # Retrieve API key securely from Render environment variables
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is missing!")
    
    # Initialize Gemini Client explicitly with the environment key
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Analyze the following cleaned content and create a new skill candidate matching the required schema.
    
    Content:
    {cleaned_content}
    
    Requirements:
    - Choose a skill_type from: 'Technical', 'Fitness', 'Finance', 'Communication'.
    - Provide a concise skill_title and a comprehensive skill_intro.
    - Generate a unique skill_id.
    - skill_holder_id and related_quest_id should initialize as empty lists `[]` unless specified.
    """
    
    try:
        # Use Structured Outputs via Gemini API with the 3.1 Flash Lite model
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "skill_id": {"type": "STRING"},
                        "skill_type": {"type": "STRING", "enum": ["Technical", "Fitness", "Finance", "Communication"]},
                        "skill_intro": {"type": "STRING"},
                        "skill_title": {"type": "STRING"},
                        "skill_holder_id": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "related_quest_id": {"type": "ARRAY", "items": {"type": "STRING"}}
                    },
                    "required": ["skill_id", "skill_type", "skill_intro", "skill_title", "skill_holder_id", "related_quest_id"]
                },
                temperature=0.2,
            ),
        )
        
        # Load the whole JSON response string directly into content
        skill_json_string = response.text
        print("Successfully generated skill candidate JSON via Gemini 3.1 Flash Lite.")
        
        skill_data = json.loads(skill_json_string)
        
        return {
            "content": skill_json_string,
            "content_id": skill_data.get("skill_id")
        }
        
    except Exception as e:
        print(f"Error generating skill via Gemini API: {e}")
        
    return state