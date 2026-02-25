from typing import Any, Callable, Optional
from .base import Component

class Text(Component):
    def __init__(self, value: str, size: int = 16, color: str = "theme.on_background") -> None:
        super().__init__(value=value, size=size, color=color)

class Button(Component):
    def __init__(
        self,
        label: str,
        on_press: Optional[Callable[..., Any]] = None,
        color: str = "theme.primary",
    ) -> None:
        super().__init__(label=label, color=color, on_press=on_press)

class Image(Component):
    def __init__(self, src: str, width: Optional[int] = None, height: Optional[int] = None) -> None:
        super().__init__(src=src, width=width, height=height)


class TextInput(Component):
    def __init__(
        self,
        name: str,
        value: str = "",
        placeholder: str = "",
        on_change: Optional[Callable[[str], Any]] = None,
    ) -> None:
        super().__init__(name=name, value=value, placeholder=placeholder, on_change=on_change)


class Form(Component):
    def __init__(
        self,
        children: Optional[list] = None,
        validators: Optional[dict] = None,
        on_submit: Optional[Callable[[dict], Any]] = None,
    ) -> None:
        super().__init__(children=children or [], validators=validators or {}, on_submit=on_submit)
        self.children = children or []
        self.validators = validators or {}
        self.on_submit = on_submit

    def validate(self) -> dict:
        errors: dict = {}
        for child in self.children:
            if hasattr(child, "props") and "name" in child.props:
                name = child.props["name"]
                val = child.props.get("value")
                if name in self.validators:
                    err = self.validators[name](val)
                    if err:
                        errors[name] = err
        return errors

    def submit(self) -> None:
        errs = self.validate()
        if errs:
            return errs
        if callable(self.on_submit):
            data = {c.props.get("name"): c.props.get("value") for c in self.children if "name" in c.props}
            self.on_submit(data)
        return {}
