import json
import re
from typing import Any


def _extract_json_object(text: str) -> dict[str, Any] | None:
    """Strip <think> blocks and code fences, then return the first valid JSON object."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = text.split("</think>")[-1].strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()

    decoder = json.JSONDecoder()
    for match in re.finditer(r"\{", text):
        try:
            obj, _ = decoder.raw_decode(text[match.start():])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def parse_gradio_json(result: Any, endpoint: str) -> dict[str, Any]:
    if isinstance(result, dict):
        parsed = result
    elif isinstance(result, str):
        if not result.strip():
            raise RuntimeError(f"Gradio endpoint {endpoint} returned an empty response.")
        if result.startswith("CPU Inference Error:"):
            raise RuntimeError(f"Gradio endpoint {endpoint} inference failed: {result}")

        parsed = _extract_json_object(result)
        if parsed is None:
            raise RuntimeError(
                f"Gradio endpoint {endpoint} returned no valid JSON. "
                f"Raw output was: {result[:200]}"
            )
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