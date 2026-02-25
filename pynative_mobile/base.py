import uuid
from typing import Any, Callable, Dict, List
from .state import State

PROP_UPDATE_LISTENERS: List[Callable[["Component", str, Any], None]] = []

class Component:
    _event_registry: Dict[str, Callable[..., Any]] = {}

    @classmethod
    def set_event_registry(cls, registry: Dict[str, Callable[..., Any]]) -> None:
        registry.update(cls._event_registry)
        cls._event_registry = registry

    def __init__(self, **kwargs: Any) -> None:
        self.id: str = str(uuid.uuid4())[:8]
        self.type: str = self.__class__.__name__
        self.props: Dict[str, Any] = {}
        self.events: Dict[str, str] = {}
        self._states: List[State] = []

        self.on_init: Any = None
        self.on_destroy: Any = None

        for key, value in kwargs.items():
            if key == "on_init" and callable(value):
                self.on_init = value
                continue
            if key == "on_destroy" and callable(value):
                self.on_destroy = value
                continue

            if callable(value):
                event_id = f"event_{str(uuid.uuid4())[:8]}"
                self._event_registry[event_id] = value
                self.events[key] = event_id
            elif hasattr(value, "bind"):
                self.props[key] = value.value
                self._states.append(value)
                value.bind(lambda v, k=key: self._update_prop(k, v))
            else:
                self.props[key] = value

    def _update_prop(self, key: str, value: Any) -> None:
        self.props[key] = value
        print(
            f">>> UI Update: Properti '{key}' pada {self.type} ({self.id}) berubah jadi '{value}'"
        )

        for listener in PROP_UPDATE_LISTENERS:
            listener(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "props": dict(self.props),
            "events": dict(self.events),
        }


class Container(Component):
    def __init__(self, children: Any = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.children: List[Component] = children or []

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["children"] = [child.to_dict() for child in self.children]
        return data