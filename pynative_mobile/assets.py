import base64
import os
from typing import Any, Dict


class AssetManager:
    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = base_path or os.getcwd()

    def resolve(self, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        if value.startswith("data:") or value.startswith("http"):
            return value
        candidate = os.path.join(self.base_path, value)
        if os.path.isfile(candidate):
            with open(candidate, "rb") as f:
                data = base64.b64encode(f.read()).decode("ascii")
            return f"data:;base64,{data}"
        return value

    def walk_tree(self, node: Dict[str, Any]) -> None:
        if "props" in node and "src" in node["props"]:
            node["props"]["src"] = self.resolve(node["props"]["src"])
        for child in node.get("children", []):
            self.walk_tree(child)
