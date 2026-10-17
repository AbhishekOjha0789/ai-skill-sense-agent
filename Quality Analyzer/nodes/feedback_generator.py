# Quality Analyzer/nodes/feedback_generator.py
from ..state import QualityAnalysisState

def feedback_generator(state: QualityAnalysisState) -> QualityAnalysisState:
    """Generates human-readable feedback and suggestions."""
    print("--- FEEDBACK GENERATOR: Creating feedback message ---")
    
    issues = []
    suggestions = []
    
    # Collect issues based on metrics
    if not state.get("schema_valid"):
        issues.append("Missing required fields in schema")
        suggestions.append("Add all required fields: " + ", ".join(state.get("missing_fields", [])))
    
    if not state.get("content_length_sufficient"):
        issues.append("Content is too brief")
        suggestions.append("Expand content with detailed explanations")
    
    if not state.get("keywords_covered"):
        issues.append("Some keywords not covered")
        suggestions.append("Ensure all keywords are mentioned in content")
    
    # Generate feedback message
    quality_score = state.get("quality_score", 0)
    if quality_score >= 0.8:
        feedback_message = "Content quality is good. Ready for use."
    elif quality_score >= 0.6:
        feedback_message = "Content needs minor improvements before use."
    else:
        feedback_message = "Content requires significant revision."
    
    return {
        **state,
        "issues_found": issues if issues else None,
        "suggestions": suggestions if suggestions else None,
        "feedback_message": feedback_message
    }
