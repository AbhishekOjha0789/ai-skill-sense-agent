from collections.abc import Callable, Mapping
from typing import Any


def _schema_shape(value: Any) -> str:
    if isinstance(value, Mapping):
        if not value:
            return "object{}"
        fields = ", ".join(
            f"{key}: {_schema_shape(item)}" for key, item in value.items()
        )
        return f"object{{{fields}}}"
    if isinstance(value, list):
        if not value:
            return "array[empty]"
        return f"array[{_schema_shape(value[0])}]"
    if value is None:
        return "null"
    return type(value).__name__


def with_schema_logging(
    node_name: str,
    node: Callable[[dict[str, Any]], dict[str, Any]],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def logged_node(state: dict[str, Any]) -> dict[str, Any]:
        print(f"[node-schema] {node_name} input: {_schema_shape(state)}")
        output = node(state)
        print(f"[node-schema] {node_name} output patch: {_schema_shape(output)}")
        return output

    return logged_node
