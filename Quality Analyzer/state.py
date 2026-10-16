from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict


class QualityAnalysisState(TypedDict):
    """
    State for the Quality Analyzer component.
    Handles quality assessment of generated content (skills or quests).
    """

    # Input from Main Agent context
    content_id: Optional[str]          # ID of the content being checked
    content_type: Optional[str]        # 'Skill' or 'Quest'
    content: Optional[Dict[str, Any]]  # The generated content to validate

    # Original request context
    user_id: Optional[str]
    keywords: Optional[List[str]]      # Requested keywords
    action_required: Optional[str]     # 'Yes' or 'No' from trigger

    # Quality metrics to track
    quality_score: Optional[float]     # Overall quality percentage (0.0 - 1.0)
    completeness_score: Optional[float]
    relevance_score: Optional[float]
    accuracy_score: Optional[float]
    consistency_score: Optional[float]

    # Detailed checks
    schema_valid: Optional[bool]       # Matches expected schema
    required_fields_present: Optional[bool]
    keywords_covered: Optional[bool]
    content_length_sufficient: Optional[bool]
    no_duplicates: Optional[bool]      # No duplicate content found

    # Results
    is_quality_approved: Optional[bool]  # 'Yes' or 'No'
    issues_found: Optional[List[str]]    # List of issues identified
    suggestions: Optional[List[str]]     # Improvement suggestions
    feedback_message: Optional[str]      # Human-readable feedback

    # Retry control
    retry_required: Optional[bool]     # Should we retry generation?
    regeneration_attempt: Optional[int]  # Current retry attempt count

    # Output flags for main workflow
    quality_status: Optional[str]      # 'Yes' or 'No' (sent back to MainAgentState)
    report_id: Optional[str]           # ID for quality report
    recommendation: Optional[str]      # 'save' or 'retry'
