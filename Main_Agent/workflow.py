from langgraph.graph import StateGraph, END
from .state import MainAgentState

# Import all individual modular nodes
from .nodes.check_database import check_database_updates
from .nodes.profile_extractor import profile_extractor
from .nodes.logs_extractor import logs_extractor
from .nodes.next_action_model import next_action_model
from .nodes.skill_allocator import skill_allocator
from .nodes.quest_allocator import quest_allocator
from .nodes.best_match_model import best_match_model
from .nodes.quality_checking_model import quality_checking_model
from .nodes.save_assignment import save_assignment
from workflow_logging import with_schema_logging


def route_after_quality_check(state: MainAgentState) -> str:
    if state.get("quality_status") != "Yes":
        return "retry"
    if state.get("best_match"):
        return "save"
    return "end"

def create_main_agent_workflow():
    workflow = StateGraph(MainAgentState)

    # 1. Add Nodes
    workflow.add_node("db_check", with_schema_logging("db_check", check_database_updates))
    workflow.add_node("profile_extractor", with_schema_logging("profile_extractor", profile_extractor))
    workflow.add_node("logs_extractor", with_schema_logging("logs_extractor", logs_extractor))
    workflow.add_node("next_action_model", with_schema_logging("next_action_model", next_action_model))
    workflow.add_node("skill_allocator", with_schema_logging("skill_allocator", skill_allocator))
    workflow.add_node("quest_allocator", with_schema_logging("quest_allocator", quest_allocator))
    workflow.add_node("best_match_model", with_schema_logging("best_match_model", best_match_model))
    workflow.add_node("quality_checking_model", with_schema_logging("quality_checking_model", quality_checking_model))
    workflow.add_node("save_assignment", with_schema_logging("save_assignment", save_assignment))

    # 2. Define Entry Point and Edges
    workflow.set_entry_point("db_check")

    # Conditional check if action is required from trigger payload
    workflow.add_conditional_edges(
        "db_check",
        lambda s: "extract" if s.get("action_required") == "Yes" else "ignore",
        {
            "extract": "profile_extractor",
            "ignore": END
        }
    )

    workflow.add_edge("profile_extractor", "logs_extractor")
    workflow.add_edge("logs_extractor", "next_action_model")

    # Route based on the Next Action Model decision ('Skill', 'Quest', or 'None')[cite: 9]
    workflow.add_conditional_edges(
        "next_action_model",
        lambda s: s.get("action", "None"),
        {
            "Skill": "skill_allocator",
            "Quest": "quest_allocator",
            "None": END
        }
    )

    # Both allocators converge into the mathematical Best Match Model
    workflow.add_edge("skill_allocator", "best_match_model")
    workflow.add_edge("quest_allocator", "best_match_model")

    workflow.add_edge("best_match_model", "quality_checking_model")

    # Quality check evaluation loop[cite: 2]
    workflow.add_conditional_edges(
        "quality_checking_model",
        route_after_quality_check,
        {
            "save": "save_assignment",
            "retry": "best_match_model",
            "end": END,
        }
    )
    workflow.add_edge("save_assignment", END)

    return workflow.compile()