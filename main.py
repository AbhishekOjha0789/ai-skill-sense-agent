from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

# Import your agent workflows as you build them
from Main_Agent.workflow import create_main_agent_workflow
from Extractor.workflow import create_extractor_workflow
# from agents.Quality_Analyzer.workflow import create_quality_analyzer_workflow

app = FastAPI(title="AI Skill Sense Agents API", version="1.0")

# Unified payload schema for Main Agent triggers
class MainAgentPayload(BaseModel):
    update_id: str
    user_id: str
    action_required: str  # "Yes" or "No"

# Payload schema for Extractor workflow triggers
class ExtractorPayload(BaseModel):
    url_id: str
    url: str
    is_visited: str  # "Yes" or "No"

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

        workflow = create_main_agent_workflow()
        result = workflow.invoke(initial_state)

        return {
            "status": "success",
            "message": f"Main Agent triggered for update_id: {payload.update_id}",
            "payload": payload.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/extractor/trigger")
async def trigger_extractor(payload: ExtractorPayload):
    """
    Receives unvisited URL info (url_id, url, is_visited: 'No') from the main backend 
    to kick off the Extractor workflow (Link Lister -> Classifier -> Crawlers -> Skill Maker).
    """
    try:
        # Check if URL has already been visited based on the schema flag
        if payload.is_visited.lower() == "yes":
            return {
                "status": "skipped",
                "message": f"URL {payload.url} has already been visited.",
                "payload": payload.dict()
            }

        initial_extractor_state = {
            "url_id": payload.url_id,
            "url": payload.url,
            "is_visited": payload.is_visited,
            "type": None,
            "cleaned": None,
            "duplicate": None,
            "content": None,
            "content_id": None,
            "matching_skill_id": None
        }

        workflow = create_extractor_workflow()
        result = workflow.invoke(initial_extractor_state)

        return {
            "status": "success",
            "message": f"Extractor workflow initiated for URL ID: {payload.url_id} ({payload.url})",
            "payload": payload.dict()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))