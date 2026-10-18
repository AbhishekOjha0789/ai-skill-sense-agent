import json
import os
import threading
import time

import httpx
from gradio_client import Client

from ..state import MainAgentState
from gradio_response import parse_gradio_json

SPACE_ID = os.getenv("HF_SPACE_ID", "AO0789/ai-skill-sense-engine")
HF_TOKEN = os.environ.get("HF_TOKEN")

READ_TIMEOUT = float(os.getenv("GRADIO_READ_TIMEOUT", "600"))  # httpx read timeout (s)
JOB_TIMEOUT = float(os.getenv("GRADIO_JOB_TIMEOUT", "420"))    # max wait per attempt (s)
MAX_ATTEMPTS = int(os.getenv("GRADIO_MAX_ATTEMPTS", "3"))
MAX_LOGS = int(os.getenv("NEXT_ACTION_MAX_LOGS", "25"))        # lower = faster CPU inference

_client = None
_client_lock = threading.Lock()


def _get_client(force_new: bool = False) -> Client:
    """Create the Gradio client once and reuse it (avoids 'Loaded as API' on every request)."""
    global _client
    with _client_lock:
        if _client is None or force_new:
            _client = Client(
                SPACE_ID,
                token=HF_TOKEN,
                verbose=False,
                httpx_kwargs={
                    "timeout": httpx.Timeout(
                        connect=60.0, read=READ_TIMEOUT, write=60.0, pool=60.0
                    )
                },
            )
        return _client


def _validate(parsed: dict) -> dict:
    """Same checks as before, raised as errors so the retry loop can try again."""
    required_fields = {"action", "skills", "quests", "keywords"}
    missing_fields = required_fields.difference(parsed)
    if missing_fields:
        raise RuntimeError(
            "Next Action Gradio response is missing fields: "
            + ", ".join(sorted(missing_fields))
        )

    action_result = parsed.get("action")
    if action_result not in {"Skill", "Quest", "None"}:
        raise RuntimeError(
            "Next Action Gradio response must include action as "
            "'Skill', 'Quest', or 'None'."
        )

    for field in ("skills", "quests", "keywords"):
        value = parsed[field]
        if not isinstance(value, list) or not all(isinstance(i, str) for i in value):
            raise RuntimeError(
                f"Next Action Gradio response field '{field}' must be a list of strings."
            )
    return parsed


def _call_space(input_text: str) -> dict:
    last_exc = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            client = _get_client(force_new=(attempt > 1))
            job = client.submit(input_text, api_name="/run_next_action")
            result = job.result(timeout=JOB_TIMEOUT)
            parsed = parse_gradio_json(result, "/run_next_action")
            return _validate(parsed)
        except Exception as exc:  # timeout, sleeping Space, bad JSON, bad schema
            last_exc = exc
            print(f"[next_action_model] attempt {attempt}/{MAX_ATTEMPTS} failed: {exc!r}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(min(5 * attempt, 15))
    raise RuntimeError(
        f"next_action_model failed after {MAX_ATTEMPTS} attempts"
    ) from last_exc


def next_action_model(state: MainAgentState) -> MainAgentState:
    print("--- NEXT ACTION MODEL: Calling Gradio client API on Hugging Face ---")

    # Gather required context from state (null-safe: state keys can exist with None)
    user_profile = state.get("profile") or {}
    user_logs = (state.get("logs") or [])[:MAX_LOGS]

    available_pool_identifiers = state.get("available_pool_identifiers") or {
        "skill_ids": user_profile.get("skills") or [],
        "quest_ids": user_profile.get("active_quests") or [],
    }

    # Input context JSON matching your training dataset structure
    input_context = {
        "user_profile": user_profile,
        "user_logs": user_logs,
        "available_pool_identifiers": available_pool_identifiers,
    }
    input_text = json.dumps(input_context, default=str)

    try:
        parsed_result = _call_space(input_text)
    except Exception as exc:
        # Safe default so one bad generation doesn't 500 the whole workflow.
        print(f"[next_action_model] giving up, returning action='None': {exc!r}")
        return {
            "action": "None",
            "skill_ids": [],
            "quest_ids": [],
            "keywords": [],
        }

    print("Successfully determined next action via Gradio API.")
    return {
        "action": parsed_result["action"],
        "skill_ids": parsed_result["skills"],
        "quest_ids": parsed_result["quests"],
        "keywords": parsed_result["keywords"],
    }