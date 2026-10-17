from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

class MainAgentState(TypedDict):
    update_id: Optional[str]
    user_id: Optional[str]
    action_required: Optional[str]  # 'Yes' or 'No'
    profile: Optional[Dict[str, Any]]
    logs: Optional[List[Dict[str, Any]]]
    action: Optional[str]           # 'Quest', 'Skill', or 'None'
    keywords: Optional[List[str]]   #
    new_skill: Optional[str]        # 'Yes' or 'No'
    skill_ids: Optional[List[str]]  #
    quest_ids: Optional[List[str]]  #
    best_match: Optional[str]       # skill_id or quest_id
    quality_status: Optional[str]   # 'Yes' or 'No'
    report_id: Optional[str]
    assignment_status: Optional[str]