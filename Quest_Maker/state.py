from typing import List, Optional, TypedDict


class QuestMakerState(TypedDict):
  skill_id: str
  skill_info: Optional[dict]
  existing_quests: Optional[List[dict]]
  generated_quests: Optional[List[dict]]
  current_quest_index: int
  error: Optional[str]