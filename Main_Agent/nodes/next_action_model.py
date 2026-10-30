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

# Only what the decision needs. email/user_id are not sent to the Space.
PROFILE_FIELDS = (
    "age", "interests", "skills", "active_quests", "completed_quest",
    "failed_quests", "summary", "occupation", "experience", "education_status",
)
LOG_FIELDS = ("log_desc", "action_required", "timestamp")

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
    if parsed.get("action") not in {"Skill", "Quest", "None"}:
        raise RuntimeError(
            "Next Action Gradio response must include action as 'Skill', 'Quest', or 'None'."
        )
    kws = parsed.get("keywords")
    if not isinstance(kws, list) or not all(isinstance(k, str) for k in kws):
        raise RuntimeError("Next Action Gradio response field 'keywords' must be a list of strings.")
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


def next_action_model(state: MainAgentState) -> MainAgentState:
    print("--- NEXT ACTION MODEL: Calling Gradio client API on Hugging Face ---")

    profile = state.get("profile") or {}
    logs = (state.get("logs") or [])[:MAX_LOGS]

    input_context = {
        "user_profile": {k: profile.get(k) for k in PROFILE_FIELDS if k in profile},
        "user_logs": [
            {k: l.get(k) for k in LOG_FIELDS if k in l} for l in logs if isinstance(l, dict)
        ],
    }
    input_text = json.dumps(input_context, default=str)

    try:
        parsed = _call_space(input_text)
    except Exception as exc:
        # The workflow ends on "None", so a Space outage looks like "no action needed".
        print(f"[next_action_model] giving up, returning action='None': {exc!r}")
        return {"action": "None", "keywords": []}

    action = parsed["action"]
    print(
        f"Next action routed: {action} "
        f"(model_action={parsed['action']}, "
        f"needs_skill={parsed.get('needs_skill')}, "
        f"needs_quest={parsed.get('needs_quest')})"
    )
    return {"action": action, "keywords": parsed["keywords"]}