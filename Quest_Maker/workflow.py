from langgraph.graph import END, StateGraph
from nodes.fetch_skill import fetch_skill
from nodes.quest_maker import quest_maker
from nodes.save_datapool import save_datapool
from state import QuestMakerState


def should_continue_saving(state: QuestMakerState) -> str:
  generated_quests = state.get("generated_quests", [])
  index = state.get("current_quest_index", 0)

  if index < len(generated_quests):
    return "save_datapool"  # Loop back to save the next quest
  return "end"


def create_quest_maker_workflow():
  workflow = StateGraph(QuestMakerState)

  workflow.add_node("fetch_skill", fetch_skill)
  workflow.add_node("quest_maker", quest_maker)
  workflow.add_node("save_datapool", save_datapool)

  workflow.set_entry_point("fetch_skill")
  workflow.add_edge("fetch_skill", "quest_maker")
  workflow.add_edge("quest_maker", "save_datapool")

  # Conditional loop edge for saving one quest at a time
  workflow.add_conditional_edges(
      "save_datapool",
      should_continue_saving,
      {"save_datapool": "save_datapool", "end": END},
  )

  return workflow.compile()