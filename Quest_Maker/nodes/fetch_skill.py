import os
import requests
from state import QuestMakerState


def fetch_skill(state: QuestMakerState) -> QuestMakerState:
  skill_id = state.get("skill_id")
  print(f"--- FETCH SKILL: Fetching details for skill_id: {skill_id} ---")

  # Use configured backend base URL or fallback to placeholder
  base_url = os.environ.get(
      "BACKEND_API_URL", "https://your-backend-api.com"
  )
  endpoint = f"{base_url}/api/skills/{skill_id}"

  try:
    # Fetch skill details using the backend contract GET /api/skills/{skill_id}
    response = requests.get(endpoint)
    response.raise_for_status()

    skill_info = response.json()
    print(f"Successfully retrieved skill info for: {skill_id}")

    return {"skill_info": skill_info, "current_quest_index": 0}

  except requests.exceptions.RequestException as e:
    print(f"Error fetching skill from backend API ({endpoint}): {e}")
    # Fallback/mock structure if network call fails during development
    fallback_skill_info = {
        "skill_id": skill_id,
        "skill_type": "Technical",
        "skill_title": "Full-Stack AI Systems",
        "skill_intro": (
            "Master building multi-agent systems and RAG architectures."
        ),
        "skill_holder_id": [],
        "related_quest_id": [],
    }
    return {"skill_info": fallback_skill_info, "current_quest_index": 0, "error": str(e)}