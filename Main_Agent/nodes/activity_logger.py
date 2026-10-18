import os

import requests


def post_activity_log(
    user_id: str,
    activity_type: str,
    log_desc: str,
    event_id: str,
) -> None:
    backend_url = os.environ.get("BACKEND_API_URL")
    agent_secret = os.environ.get("AGENT_SECRET_KEY")
    if not backend_url:
        raise RuntimeError("BACKEND_API_URL environment variable is missing.")
    if not agent_secret:
        raise RuntimeError("AGENT_SECRET_KEY environment variable is missing.")

    response = requests.post(
        f"{backend_url.rstrip('/')}/api/webhooks/activities",
        json={
            "user_id": user_id,
            "activity_type": activity_type,
            "log_desc": log_desc,
            "event_id": event_id,
        },
        headers={"X-Agent-Secret": agent_secret},
        timeout=30,
    )
    response.raise_for_status()
