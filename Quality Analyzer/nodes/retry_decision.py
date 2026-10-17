# Quality Analyzer/nodes/retry_decision.py
from ..state import QualityAnalysisState

def retry_decision(state: QualityAnalysisState) -> QualityAnalysisState:
    """Determines if retry is required and recommends action."""
    print("--- RETRY DECISION: Determining next action ---")
    
    quality_score = state.get("quality_score", 0)
    retry_required = quality_score < 0.6  # Threshold for retry
    
    # Determine recommendation
    if retry_required:
        recommendation = "retry"
        retry_count = (state.get("regeneration_attempt") or 0) + 1
    else:
        recommendation = "save"
        retry_count = 0
    
    return {
        **state,
        "retry_required": retry_required,
        "regeneration_attempt": retry_count,
        "recommendation": recommendation,
        "is_quality_approved": not retry_required
    }
