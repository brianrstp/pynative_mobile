from .engine import PyNativeApp
from .state import State
import json
from typing import Any, Optional


class HardwarePlugin:
    def __init__(self, app: PyNativeApp):
        self.app = app

    def _request(self, action: str, payload: Optional[Any] = None) -> State:
        state = State(None)
        eid = f"hardware_{action}_{id(state)}"

        def _response(data: Any = None) -> None:
            state.value = data

        self.app.event_registry[eid] = _response

        packet = json.dumps({"type": "hardware", "action": action, "payload": payload, "response_id": eid})
        if self.app.bridge:
            self.app.bridge.broadcast(packet)
        else:
            print("[Hardware] no bridge available, cannot send request")

        return state

    def request_permission(self, permission: str) -> State:
        return self._request("permission", permission)

    def open_camera(self) -> State:
        return self._request("camera")

    def get_location(self) -> State:
        return self._request("location")

def Hardware(app: PyNativeApp) -> HardwarePlugin:
    return HardwarePlugin(app)
