# Quality Analyzer/nodes/quality_scorer.py
from ..state import QualityAnalysisState

def quality_scorer(state: QualityAnalysisState) -> QualityAnalysisState:
    """Calculates weighted quality score."""
    print("--- QUALITY SCORER: Calculating quality metrics ---")
    
    # Scoring weights (can be configured)
    W_SCHEMA = 0.30
    W_LENGTH = 0.20
    W_KEYWORDS = 0.20
    W_DEPTH = 0.15
    W_DUPLICATES = 0.15
    
    # Get individual scores (0.0 - 1.0)
    schema_score = 1.0 if state.get("schema_valid") else 0.0
    length_score = 1.0 if state.get("content_length_sufficient") else 0.5
    keywords_score = 1.0 if state.get("keywords_covered") else 0.5
    depth_score = 0.8  # Placeholder - would analyze actual content depth
    duplicate_score = 1.0 if state.get("no_duplicates") else 0.3
    
    # Calculate weighted total
    quality_score = (
        W_SCHEMA * schema_score +
        W_LENGTH * length_score +
        W_KEYWORDS * keywords_score +
        W_DEPTH * depth_score +
        W_DUPLICATES * duplicate_score
    )
    
    return {
        **state,
        "quality_score": round(quality_score, 3),
        "completeness_score": round(length_score, 3),
        "relevance_score": round(keywords_score, 3),
        "accuracy_score": round(schema_score, 3),
        "consistency_score": round(depth_score, 3)
    }
