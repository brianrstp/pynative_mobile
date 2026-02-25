from typing import Dict

class Theme:
    def __init__(
        self,
        primary: str = "#6200EE",
        background: str = "#FFFFFF",
        on_background: str = "#000000",
    ) -> None:
        self.colors: Dict[str, str] = {
            "primary": primary,
            "background": background,
            "on_background": on_background,
        }

    def to_dict(self) -> Dict[str, Dict[str, str]]:
        return {"colors": self.colors}

default_theme = Theme()