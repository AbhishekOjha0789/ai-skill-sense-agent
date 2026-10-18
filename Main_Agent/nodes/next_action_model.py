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

READ_TIMEOUT = float(os.getenv("GRADIO_READ_TIMEOUT", "600"))
JOB_TIMEOUT = float(os.getenv("GRADIO_JOB_TIMEOUT", "420"))
MAX_ATTEMPTS = int(os.getenv("GRADIO_MAX_ATTEMPTS", "2"))
MAX_LOGS = int(os.getenv("NEXT_ACTION_MAX_LOGS", "10"))  # fewer logs = faster CPU inference

# Only the fields present in the training data
PROFILE_FIELDS = (
    "user_id", "username", "email", "age", "gender", "interests", "skills",
    "active_quests", "completed_quest", "failed_quests", "summary",
)
LOG_FIELDS = ("user_id", "log_id", "log_desc", "action_required", "timestamp")

_client = None
_client_lock = threading.Lock()


def _get_client(force_new: bool = False) -> Client:
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
    required_fields = {"action", "skills", "quests", "keywords"}
    missing_fields = required_fields.difference(parsed)
    if missing_fields:
        raise RuntimeError(
            "Next Action Gradio response is missing fields: "
            + ", ".join(sorted(missing_fields))
        )
    if parsed.get("action") not in {"Skill", "Quest", "None"}:
        raise RuntimeError(
            "Next Action Gradio response must include action as 'Skill', 'Quest', or 'None'."
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
            return _validate(parse_gradio_json(result, "/run_next_action"))
        except Exception as exc:
            last_exc = exc
            print(f"[next_action_model] attempt {attempt}/{MAX_ATTEMPTS} failed: {exc!r}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(5)
    raise RuntimeError(f"next_action_model failed after {MAX_ATTEMPTS} attempts") from last_exc


def _only_pool(items, pool) -> list:
    """Drop IDs the model invented: the training task is 'IDs present in the input'."""
    pool = set(pool)
    return [i for i in items if i in pool]


def next_action_model(state: MainAgentState) -> MainAgentState:
    print("--- NEXT ACTION MODEL: Calling Gradio client API on Hugging Face ---")

    profile = state.get("profile") or {}
    logs = (state.get("logs") or [])[:MAX_LOGS]

    user_profile = {k: profile.get(k) for k in PROFILE_FIELDS if k in profile}
    user_logs = [
        {k: l.get(k) for k in LOG_FIELDS if k in l} for l in logs if isinstance(l, dict)
    ]

    # TODO: this should be the full pool of available skill/quest IDs from your DB,
    # not the user's own items. See note below.
    pool = state.get("available_pool_identifiers") or {
        "skill_ids": profile.get("skills") or [],
        "quest_ids": profile.get("active_quests") or [],
    }

    input_context = {
        "user_profile": user_profile,
        "user_logs": user_logs,
        "available_pool_identifiers": pool,
    }
    input_text = json.dumps(input_context, default=str)  # default separators, as in training

    try:
        parsed = _call_space(input_text)
    except Exception as exc:
        print(f"[next_action_model] giving up, returning action='None': {exc!r}")
        return {"action": "None", "skill_ids": [], "quest_ids": [], "keywords": []}

    skills = _only_pool(parsed["skills"], pool.get("skill_ids") or [])
    quests = _only_pool(parsed["quests"], pool.get("quest_ids") or [])

    print("Successfully determined next action via Gradio API.")
    return {
        "action": parsed["action"],
        "skill_ids": skills,
        "quest_ids": quests,
        "keywords": parsed["keywords"],
    }