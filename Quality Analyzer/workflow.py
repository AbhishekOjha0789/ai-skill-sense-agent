from langgraph.graph import StateGraph, END
from state import QualityAnalysisState

# Import all individual modular nodes
from .nodes.schema_validator import schema_validator
from .nodes.content_analyzer import content_analyzer
from .nodes.quality_scorer import quality_scorer
from .nodes.feedback_generator import feedback_generator
from .nodes.retry_decision import retry_decision

def create_quality_analyzer_workflow():
    workflow = StateGraph(QualityAnalysisState)
    
    # 1. Add Nodes
    workflow.add_node("schema_validator", schema_validator)
    workflow.add_node("content_analyzer", content_analyzer)
    workflow.add_node("quality_scorer", quality_scorer)
    workflow.add_node("feedback_generator", feedback_generator)
    workflow.add_node("retry_decision", retry_decision)
    
    # 2. Define Entry Point and Edges
    workflow.set_entry_point("schema_validator")
    
    # Sequential processing pipeline
    workflow.add_edge("schema_validator", "content_analyzer")
    workflow.add_edge("content_analyzer", "quality_scorer")
    workflow.add_edge("quality_scorer", "feedback_generator")
    workflow.add_edge("feedback_generator", "retry_decision")
    
    # Conditional retry loop
    workflow.add_conditional_edges(
        "retry_decision",
        lambda s: "retry" if s.get("retry_required") == True else "end",
        {
            "retry": "schema_validator",  # Loop back for regeneration
            "end": END
        }
    )
    
    return workflow.compile()

# Compiled application ready to be invoked
app_workflow = create_quality_analyzer_workflow()
