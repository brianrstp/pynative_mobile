from typing import Any, List, Optional
from .base import Container


class Column(Container):
    def __init__(self, children: Optional[List[Any]] = None, spacing: int = 10) -> None:
        super().__init__(children=children, spacing=spacing)

class Row(Container):
    def __init__(self, children: Optional[List[Any]] = None, spacing: int = 10) -> None:
        super().__init__(children=children, spacing=spacing)

class Screen(Container):
    def __init__(self, title: str = "PyNative App", children: Optional[List[Any]] = None) -> None:
        super().__init__(children=children, title=title)