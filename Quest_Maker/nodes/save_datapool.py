import os
import requests
from ..state import QuestMakerState

BACKEND_API_URL = os.environ.get(
    "BACKEND_API_URL"
)
AGENT_SECRET_KEY = os.getenv("AGENT_SECRET_KEY")


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

        if not BACKEND_API_URL:
            raise RuntimeError("BACKEND_API_URL environment variable is missing.")
        backend_url = (
            f"{BACKEND_API_URL.rstrip('/')}/api/datapool/quests/create"
        )

        if not AGENT_SECRET_KEY:
            raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")
        headers = {"X-Agent-Secret": AGENT_SECRET_KEY}

        try:
            response = requests.post(
                backend_url,
                json=current_quest,
                headers=headers,
                timeout=40,
            )
            response.raise_for_status()
            print(f"[*] Quest saved successfully: {current_quest.get('quest_name')}")

            # Increment index ONLY on success
            state["current_quest_index"] = index + 1

        except requests.RequestException as e:
            error_msg = (
                f"Failed to save quest '{current_quest.get('quest_name')}' "
                f"to backend: {e}"
            )
            print(error_msg)
            state["error"] = error_msg
            raise RuntimeError(error_msg) from e

    return state