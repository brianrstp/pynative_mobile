from typing import Any, Callable, List


class State:
    def __init__(self, initial_value: Any) -> None:
        self._value: Any = initial_value
        self._listeners: List[Callable[[Any], None]] = []

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, new_val: Any) -> None:
        self._value = new_val
        for listener in list(self._listeners):
            listener(new_val)

    def bind(self, callback: Callable[[Any], None]) -> Callable[[], None]:
        self._listeners.append(callback)
        def _unbind() -> None:
            if callback in self._listeners:
                self._listeners.remove(callback)
        return _unbind

    def __str__(self) -> str:
        return str(self._value)