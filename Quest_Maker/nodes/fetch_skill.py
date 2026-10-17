import os
import requests
from ..state import QuestMakerState


def fetch_skill(state: QuestMakerState) -> QuestMakerState:
  skill_id = state.get("skill_id")
  print(f"--- FETCH SKILL: Fetching details for skill_id: {skill_id} ---")

  # Use configured backend base URL or fallback to placeholder
  base_url = os.environ.get(
      "BACKEND_API_URL"
  )
  agent_secret = os.environ.get("AGENT_SECRET_KEY")
  if not base_url:
    raise RuntimeError("BACKEND_API_URL environment variable is missing.")
  if not agent_secret:
    raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
  endpoint = f"{base_url.rstrip('/')}/api/skills/{skill_id}"

  response = requests.get(
      endpoint,
      headers={"X-Agent-Secret": agent_secret},
      timeout=30,
  )
  response.raise_for_status()
  skill_info = response.json()
  print(f"Successfully retrieved skill info for: {skill_id}")

  return {"skill_info": skill_info, "current_quest_index": 0}