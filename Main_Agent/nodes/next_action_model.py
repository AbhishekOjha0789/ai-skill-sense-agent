import json
import os
from gradio_client import Client
from ..state import MainAgentState

def next_action_model(state: MainAgentState) -> MainAgentState:
    print("--- NEXT ACTION MODEL: Calling Gradio client API on Hugging Face ---")
    
    # Gather required context from state
    user_profile = state.get("profile", {})
    user_logs = state.get("logs", [])
    
    # Fetch available pool identifiers from backend or state (mocked or pre-fetched if stored in state)
    # Falling back to empty or state-provided identifiers
    available_pool_identifiers = state.get("available_pool_identifiers", {
        "skill_ids": user_profile.get("skills", []),
        "quest_ids": user_profile.get("active_quests", [])
    })

    # Construct the input context JSON matching your training dataset structure
    input_context = {
        "user_profile": user_profile,
        "user_logs": user_logs,
        "available_pool_identifiers": available_pool_identifiers
    }

    input_text = json.dumps(input_context)
    hf_token = os.environ.get("HF_TOKEN")
    client = Client("AO0789/ai-skill-sense-engine", token=hf_token)
    result = client.predict(
        input_text,
        api_name="/run_next_action",
    )

    if isinstance(result, str):
        try:
            parsed_result = json.loads(result)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Next Action Gradio endpoint returned invalid JSON "
                f"(line {exc.lineno}, column {exc.colno})."
            ) from exc
    elif isinstance(result, dict):
        parsed_result = result
    else:
        raise RuntimeError(
            "Next Action Gradio endpoint returned an unsupported response "
            f"type: {type(result).__name__}."
        )

    if not isinstance(parsed_result, dict):
        raise RuntimeError(
            "Next Action Gradio endpoint must return a JSON object."
        )

    action_result = parsed_result.get("action")
    if action_result not in {"Skill", "Quest", "None"}:
        raise RuntimeError(
            "Next Action Gradio response must include action as "
            "'Skill', 'Quest', or 'None'."
        )

    skills_result = parsed_result.get("skills", [])
    quests_result = parsed_result.get("quests", [])
    keywords_result = parsed_result.get("keywords", [])
    for field, value in (
        ("skills", skills_result),
        ("quests", quests_result),
        ("keywords", keywords_result),
    ):
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise RuntimeError(
                f"Next Action Gradio response field '{field}' must be "
                "a list of strings."
            )

    print("Successfully determined next action via Gradio API.")
    return {
        "action": action_result,
        "skill_ids": skills_result,
        "quest_ids": quests_result,
        "keywords": keywords_result
    }