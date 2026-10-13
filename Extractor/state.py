# state.py
from typing import TypedDict, Literal, Optional

class AgentState(TypedDict):
    url: str
    url_id: Optional[str]
    type: Literal["Image", "Audio", "Web", None]
    cleaned: Literal["Yes", "No", None]
    duplicate: Literal["Yes", "No", None]
    is_visited: Literal["Yes", "No", None]
    content: Optional[str]
    content_id: Optional[str]
    matching_skill_id: Optional[str]