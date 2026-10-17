import hmac
import os

from fastapi import Header, HTTPException, status


def require_agent_secret(
    x_agent_secret: str | None = Header(default=None, alias="X-Agent-Secret"),
) -> None:
    configured_secret = os.environ.get("AGENT_SECRET_KEY")
    if not configured_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent-to-agent authentication is not configured.",
        )

    if not x_agent_secret or not hmac.compare_digest(
        x_agent_secret, configured_secret
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent secret key.",
        )
