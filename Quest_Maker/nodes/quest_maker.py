import json
import os
from datetime import datetime
from google import genai
from google.genai import types
from ..state import QuestMakerState


def quest_maker(state: QuestMakerState) -> QuestMakerState:
  print(
      "--- QUEST MAKER: Generating exactly 5 quests via Gemini 3.5 Flash ---"
  )
  skill_info = state.get("skill_info", {})
  skill_id = state.get("skill_id", "unknown_skill")

  api_key = os.environ.get("GEMINI_API_KEY")
  if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable is missing!")

  client = genai.Client(api_key=api_key)

  prompt = f"""
    Analyze the following skill information and create **exactly 5 progressive quests** for it.
    
    Skill Info:
    {json.dumps(skill_info, indent=2)}
    
    Requirements:
    - Generate unique quest IDs.
    - Set seq_no sequentially from 1 to 5.
    - linked_skill must include the current skill_id: ["{skill_id}"].
    - quest_type must be one of: 'Learning', 'Webhook', 'Location', 'Physical'.
    - scale must be one of: 'seconds', 'calories', 'others'.
    - quest_metrics should be a float value representing target goals.
    - quest_holder_id should initialize as an empty list [].
    - duration should be time in seconds given to complete the quest.
    - last_update should be the current timestamp in ISO 8601 format.
    """

  try:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "quests": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "quest_id": {"type": "STRING"},
                                "seq_no": {"type": "INTEGER"},
                                "linked_skill": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"},
                                },
                                "quest_name": {"type": "STRING"},
                                "quest_desc": {"type": "STRING"},
                                "quest_type": {
                                    "type": "STRING",
                                    "enum": [
                                        "Learning",
                                        "Webhook",
                                        "Location",
                                        "Physical",
                                    ],
                                },
                                "scale": {
                                    "type": "STRING",
                                    "enum": ["seconds", "calories", "others"],
                                },
                                "quest_metrics": {"type": "NUMBER"},
                                "template": {"type": "STRING"},
                                "last_update": {"type": "STRING"},
                                "quest_holder_id": {
                                    "type": "ARRAY",
                                    "items": {"type": "STRING"},
                                },
                                "duration": {"type": "INTEGER"},
                            },
                            "required": [
                                "quest_id",
                                "seq_no",
                                "linked_skill",
                                "quest_name",
                                "quest_desc",
                                "quest_type",
                                "scale",
                                "quest_metrics",
                                "template",
                                "last_update",
                                "quest_holder_id",
                                "duration",
                            ],
                        },
                    }
                },
                "required": ["quests"],
            },
            temperature=0.3,
        ),
    )

    result_data = json.loads(response.text)
    generated_quests = result_data.get("quests", [])[:5]  # Enforce max 5 limit
    print(f"Successfully generated {len(generated_quests)} quests.")

    return {"generated_quests": generated_quests}

  except Exception as e:
    print(f"Error generating quests via Gemini API: {e}")
    raise RuntimeError("Quest generation failed.") from e