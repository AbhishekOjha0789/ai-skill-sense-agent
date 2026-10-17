# Quality Analyzer/nodes/schema_validator.py
from ..state import QualityAnalysisState

def schema_validator(state: QualityAnalysisState) -> QualityAnalysisState:
    """Validates content against expected schema."""
    print("--- SCHEMA VALIDATOR: Checking content against expected schema ---")
    
    content = state.get("content", {})
    content_type = state.get("content_type", "Skill")
    
    # Define expected schema based on content type
    if content_type == "Skill":
        required_fields = ["name", "description", "keywords", "skill_id", 
                          "equivalent_skills", "category", "complexity", "difficulty"]
    else:  # Quest
        required_fields = ["name", "description", "keywords", "questId",
                          "type", "difficulty", "duration", "rewards"]
    
    # Perform schema validation
    schema_valid = all(field in content for field in required_fields)
    missing_fields = [field for field in required_fields if field not in content]
    
    return {
        **state,
        "schema_valid": schema_valid,
        "missing_fields": missing_fields if missing_fields else None
    }
