import json
from typing import Any


def parse_gradio_json(result: Any, endpoint: str) -> dict[str, Any]:
    if isinstance(result, dict):
        parsed = result
    elif isinstance(result, str):
        if not result.strip():
            raise RuntimeError(f"Gradio endpoint {endpoint} returned an empty response.")
        if result.startswith("CPU Inference Error:"):
            raise RuntimeError(
                f"Gradio endpoint {endpoint} inference failed: {result}"
            )
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Gradio endpoint {endpoint} returned invalid JSON "
                f"(line {exc.lineno}, column {exc.colno})."
            ) from exc
    else:
        raise RuntimeError(
            f"Gradio endpoint {endpoint} returned unsupported response type "
            f"{type(result).__name__}."
        )

    if not isinstance(parsed, dict):
        raise RuntimeError(f"Gradio endpoint {endpoint} must return a JSON object.")
    print(
        f"[gradio-schema] {endpoint} response fields: "
        f"{', '.join(parsed.keys()) or '(none)'}"
    )
    return parsed
