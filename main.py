import asyncio
from dotenv import load_dotenv
from typing import Literal
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
  
# Load environment variables
load_dotenv()

# Import your agent workflows
from Extractor.workflow import create_extractor_workflow
from Main_Agent.workflow import create_main_agent_workflow
from Quest_Maker.workflow import create_quest_maker_workflow
from security import require_agent_secret

# from agents.Quality_Analyzer.workflow import create_quality_analyzer_workflow

app = FastAPI(title="AI Skill Sense Agents API", version="1.0")


# Unified payload schema for Main Agent triggers
class MainAgentPayload(BaseModel):
  update_id: str
  user_id: str
  action_required: Literal["Yes", "No"]


# Payload schema for Extractor workflow triggers
class ExtractorPayload(BaseModel):
  url_id: str
  url: str
  is_visited: Literal["Yes", "No"]


# Payload schema for Quest Maker workflow triggers
class QuestMakerPayload(BaseModel):
  skill_id: str


@app.get("/")
async def root():
  return {"status": "AI Skill Sense Agent Service is running"}


@app.post("/agents/main-agent/trigger")
async def trigger_main_agent(
    payload: MainAgentPayload,
    _: None = Depends(require_agent_secret),
):
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
        "report_id": None,
        "assignment_status": None,
    }

    workflow = create_main_agent_workflow()

    # Offload blocking workflow invocation to a separate thread pool
    result = await asyncio.to_thread(workflow.invoke, initial_state)

    return {
        "status": "success",
        "message": (
            f"Main Agent triggered for update_id: {payload.update_id}"
        ),
        "payload": payload.model_dump(),
        "result": result,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/extractor/trigger")
async def trigger_extractor(
    payload: ExtractorPayload,
    _: None = Depends(require_agent_secret),
):
  """Receives unvisited URL info from the main backend to kick off the Extractor workflow."""
  try:
    if payload.is_visited == "Yes":
      return {
          "status": "skipped",
          "message": f"URL {payload.url} has already been visited.",
          "payload": payload.model_dump(),
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
        "matching_skill_id": None,
    }

    workflow = create_extractor_workflow()

    # Offload blocking extractor workflow invocation
    result = await asyncio.to_thread(workflow.invoke, initial_extractor_state)

    return {
        "status": "success",
        "message": (
            "Extractor workflow initiated for URL ID:"
            f" {payload.url_id} ({payload.url})"
        ),
        "payload": payload.model_dump(),
        "result": result,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/quest-maker/trigger")
async def trigger_quest_maker(
    payload: QuestMakerPayload,
    _: None = Depends(require_agent_secret),
):
  """Receives backend nudge with skill_id to initiate the Quest Maker workflow."""
  try:
    initial_quest_state = {
        "skill_id": payload.skill_id,
        "skill_info": None,
        "existing_quests": None,
        "generated_quests": None,
        "current_quest_index": 0,
        "error": None,
    }

    workflow = create_quest_maker_workflow()

    # Offload blocking quest maker workflow invocation
    result = await asyncio.to_thread(workflow.invoke, initial_quest_state)

    return {
        "status": "success",
        "message": (
            f"Quest Maker workflow completed for skill_id: {payload.skill_id}"
        ),
        "payload": payload.model_dump(),
        "result": result,
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))