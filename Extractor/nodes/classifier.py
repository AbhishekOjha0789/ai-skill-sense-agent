# nodes/classifier.py
from ..state import AgentState

def classifier(state: AgentState) -> AgentState:
    print("--- CLASSIFIER: Determining file/content type ---")
    target_url = state.get("url", "").lower()
    
    # Simple content-type detection logic based on extension or URL patterns
    # (Can be expanded with a lightweight classifier model or HTTP header check)
    if target_url.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif")):
        content_type = "Image"
    elif target_url.endswith((".mp3", ".wav", ".m4a", ".aac", ".ogg")):
        content_type = "Audio"
    else:
        content_type = "Web"  # Default fallback for websites, articles, etc.
        
    print(f"Classified type as: {content_type}")
    
    return {
        "type": content_type
    }