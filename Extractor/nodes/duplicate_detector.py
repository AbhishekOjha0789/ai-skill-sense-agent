# nodes/duplicate_detector.py
import os
import json
import requests
from ..state import AgentState

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
        
        backend_url = os.environ.get("BACKEND_API_URL")
        if not backend_url:
            raise RuntimeError("BACKEND_API_URL environment variable is missing.")
        agent_secret = os.environ.get("AGENT_SECRET_KEY")
        if not agent_secret:
            raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
        endpoint = f"{backend_url}/api/skills/by-type"
        
        # 1. Fetch existing skills of the same type to compare intro text
        response = requests.post(
            endpoint,
            json={"skill_type": skill_type},
            headers={"X-Agent-Secret": agent_secret},
            timeout=30,
        )
        response.raise_for_status()

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

        if max_match_score >= 0.75 and best_match_id:
            print("Match >= 75%. Routing to Skill Enhancement Model.")
            return {
                "duplicate": "Yes",
                "matching_skill_id": best_match_id,
            }
        print("Match < 75%. Treating as a unique new skill to insert.")
        return {
            "duplicate": "No",
            "matching_skill_id": None,
        }
    except (requests.RequestException, ValueError, TypeError) as exc:
        raise RuntimeError("Skill duplicate check failed.") from exc