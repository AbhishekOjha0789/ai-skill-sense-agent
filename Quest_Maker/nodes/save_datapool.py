import requests
from state import QuestMakerState


def save_datapool(state: QuestMakerState) -> QuestMakerState:
  print(
      "--- SAVE DATAPOOL: Saving one quest at a time to backend DataPool ---"
  )
  generated_quests = state.get("generated_quests", [])
  index = state.get("current_quest_index", 0)

  if index < len(generated_quests):
    current_quest = generated_quests[index]
    print(
        f"[*] Saving Quest {index + 1}/{len(generated_quests)}:"
        f" {current_quest.get('quest_name')}"
    )

    # Dummy backend URL (can be changed later)
    backend_url = "https://your-backend-api.com/api/datapool/quests/create"

    try:
      # In production, send POST request for the single quest
      response = requests.post(backend_url, json=current_quest)
      response.raise_for_status()
      print(f"[*] Quest saved successfully: {current_quest.get('quest_name')}")
      
    except Exception as e:
      print(f"Error saving quest to backend: {e}")

    # Increment index for the loop routing
    state["current_quest_index"] = index + 1

  return state