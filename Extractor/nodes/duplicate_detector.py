# nodes/duplicate_detector.py
import os
import json
import requests
from state import AgentState

def calculate_token_match(intro_a: str, intro_b: str) -> float:
    """Calculates the percentage token overlap between two strings."""
    tokens_a = set(intro_a.lower().split())
    tokens_b = set(intro_b.lower().split())
    
    if not tokens_a or not tokens_b:
        return 0.0
        
    intersection = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    
    # Jaccard similarity or token overlap ratio
    overlap_ratio = len(intersection) / len(union)
    return overlap_ratio

def duplicate_detector(state: AgentState) -> AgentState:
    print("--- DUPLICATE DETECTOR: Fetching skills and checking 75% intro token match ---")
    
    content_str = state.get("content", "{}")
    
    try:
        new_skill = json.loads(content_str)
        new_intro = new_skill.get("skill_intro", "")
        skill_type = new_skill.get("skill_type", "")
        
        backend_url = os.environ.get("BACKEND_API_URL", "https://your-backend-api.com")
        endpoint = f"{backend_url}/api/skills/by-type"
        
        # 1. Fetch existing skills of the same type to compare intro text
        response = requests.post(endpoint, json={"skill_type": skill_type}, timeout=10)
        
        if response.status_code == 200:
            existing_skills = response.json().get("skills", [])
            
            best_match_id = None
            max_match_score = 0.0
            
            for ext_skill in existing_skills:
                ext_intro = ext_skill.get("skill_intro", "")
                score = calculate_token_match(new_intro, ext_intro)
                
                if score > max_match_score:
                    max_match_score = score
                    best_match_id = ext_skill.get("skill_id")
            
            print(f"Highest token match score found: {max_match_score * 100:.2f}%")
            
            # 2. Check if token match is 75% (0.75) or higher
            if max_match_score >= 0.75 and best_match_id:
                print("Match >= 75%. Routing to Skill Enhancement Model.")
                return {
                    "duplicate": "Yes",
                    "matching_skill_id": best_match_id,
                }
            else:
                print("Match < 75%. Treating as a unique new skill to insert.")
                return {
                    "duplicate": "No",
                    "matching_skill_id": None,
                }
                
    except Exception as e:
        print(f"Error during token match duplicate detection: {e}")
        
    return {
        "duplicate": "No",
        "matching_skill_id": None
    }