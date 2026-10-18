import json
import re
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
            
        cleaned_result = result.strip()
        
        # 1. Strip markdown code blocks if the model wrapped the JSON in them
        if cleaned_result.startswith("```"):
            cleaned_result = re.sub(r"^```(?:json)?\s*", "", cleaned_result, flags=re.IGNORECASE)
            cleaned_result = re.sub(r"\s*```$", "", cleaned_result)
            cleaned_result = cleaned_result.strip()
            
        # 2. Fallback: If there's surrounding text, extract the first JSON object block
        try:
            parsed = json.loads(cleaned_result)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", cleaned_result, re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except json.JSONDecodeError as exc:
                    raise RuntimeError(
                        f"Gradio endpoint {endpoint} returned invalid JSON "
                        f"(line {exc.lineno}, column {exc.colno}). Raw output was: {result[:200]}"
                    ) from exc
            else:
                raise RuntimeError(
                    f"Gradio endpoint {endpoint} returned invalid JSON "
                    f"and no JSON object could be extracted. Raw output was: {result[:200]}"
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