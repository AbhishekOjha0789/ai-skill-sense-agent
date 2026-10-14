from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import your agent workflows as you build them
# from agents.Main_Agent.workflow import create_main_agent_workflow
# from agents.Extractor.workflow import create_extractor_workflow
# from agents.Quality_Analyzer.workflow import create_quality_analyzer_workflow

app = FastAPI(title="AI Skill Sense Agents API", version="1.0")

# Unified payload schema for Main Agent triggers
class MainAgentPayload(BaseModel):
    update_id: str
    user_id: str
    action_required: str  # "Yes" or "No"

@app.get("/")
async def root():
    return {"status": "AI Skill Sense Agent Service is running"}

@app.post("/agents/main-agent/trigger")
async def trigger_main_agent(payload: MainAgentPayload):
    try:
        initial_state = {
            "update_id": payload.update_id,
            "user_id": payload.user_id,
            "action_required": payload.action_required,
            "profile": None,
            "logs": None,
            "action": None,
            "keywords": None,
            "new_skill": None,
            "skill_ids": None,
            "quest_ids": None,
            "best_match": None,
            "quality_status": None,
            "report_id": None
        }

        # workflow = create_main_agent_workflow()
        # result = workflow.invoke(initial_state)

        return {
            "status": "success",
            "message": f"Main Agent triggered for update_id: {payload.update_id}",
            "payload": payload.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# You can add similar endpoints for Extractor or Quality Analyzer here in the future