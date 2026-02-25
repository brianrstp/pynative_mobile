import json
from typing import Any, Callable, Dict, List
from .theme import default_theme
from .base import Component, Container, PROP_UPDATE_LISTENERS
from .assets import AssetManager
from .transport import BridgeServer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os, threading

class PyNativeApp:
    def __init__(
        self,
        root: Component,
        theme: Any = None,
        start_server: bool = False,
        watch_path: str | None = None,
    ) -> None:
        self.stack: List[Component] = [root]
        self.root: Component = root
        self.theme = theme or default_theme
        self.event_registry: Dict[str, Callable[..., Any]] = {}
        Component.set_event_registry(self.event_registry)
        self.assets = AssetManager()

        from .hardware import Hardware
        from .storage import Storage

        self.hardware = Hardware(self)
        self.storage = Storage()
        self.bridge: BridgeServer | None = None
        self.store: Dict[str, Any] = {}
        self._middleware: List[Callable[[Dict[str, Any]], None]] = []

        if start_server:
            self.start_bridge()
        if watch_path:
            self._start_watcher(watch_path)
        PROP_UPDATE_LISTENERS.append(lambda *_: self.notify_bridge())
        self._setup_state_listeners(root)

    def build(self) -> str:
        payload = {
            "metadata": {"version": "0.1.0", "engine": "PyNative-Core"},
            "theme": self.theme.to_dict(),
            "tree": self.root.to_dict(),
        }
        self.assets.walk_tree(payload["tree"])
        return json.dumps(payload, indent=4)

    def _setup_state_listeners(self, component: Component) -> None:
        if hasattr(component, "_states"):
            for state in component._states:
                state.bind(lambda _, s=state: self.notify_bridge())
        if isinstance(component, Container):
            for child in component.children:
                self._setup_state_listeners(child)

    def notify_bridge(self) -> None:
        for mw in self._middleware:
            try:
                mw(self)
            except Exception as e:
                print(f"[Middleware error] {e}")

        print("\n[PyNative Bridge] Sinyal Perubahan Diterima!")
        new_tree = self.get_tree()
        packet = None

        if getattr(self, "_last_tree", None) is None:
            packet = self.build()
        else:
            patches = self._diff_trees(self._last_tree, new_tree)
            if patches:
                packet = json.dumps({"patches": patches}, indent=4)
        self._last_tree = new_tree

        print("[PyNative Bridge] Mengirim data terbaru ke HP...")
        if packet and self.bridge:
            self.bridge.broadcast(packet)

    def use_middleware(self, func: Callable[["PyNativeApp"], None]) -> None:
        self._middleware.append(func)

    def get_tree(self) -> Dict[str, Any]:
        return self.root.to_dict()

    def _diff_trees(self, old: Dict[str, Any], new: Dict[str, Any]) -> List[Dict[str, Any]]:
        patches: List[Dict[str, Any]] = []

        if old.get("id") != new.get("id") or old.get("type") != new.get("type"):
            patches.append({"action": "replace", "old": old, "new": new})
            return patches

        old_props = old.get("props", {})
        new_props = new.get("props", {})

        for k, v in new_props.items():
            if k not in old_props or old_props[k] != v:
                patches.append({"action": "update", "id": new["id"], "prop": k, "value": v})

        for k in old_props:
            if k not in new_props:
                patches.append({"action": "remove_prop", "id": new["id"], "prop": k})

        o_children = old.get("children", [])
        n_children = new.get("children", [])

        o_map = {c.get("props", {}).get("key"): c for c in o_children if c.get("props", {}).get("key")}
        n_map = {c.get("props", {}).get("key"): c for c in n_children if c.get("props", {}).get("key")}
        if o_map and n_map:
            for key, nnode in n_map.items():
                onode = o_map.get(key)
                if onode:
                    patches.extend(self._diff_trees(onode, nnode))
                else:
                    patches.append({"action": "add", "parent": new["id"], "component": nnode})
            for key, onode in o_map.items():
                if key not in n_map:
                    patches.append({"action": "remove", "id": onode["id"]})
        else:
            for i, (o, n) in enumerate(zip(o_children, n_children)):
                patches.extend(self._diff_trees(o, n))

            if len(n_children) > len(o_children):
                for c in n_children[len(o_children) :]:
                    patches.append({"action": "add", "parent": new["id"], "component": c})

            if len(o_children) > len(n_children):
                for o in o_children[len(n_children) :]:
                    patches.append({"action": "remove", "id": o["id"]})

        return patches

    def start_bridge(self, host: str = "0.0.0.0", port: int = 8000, *,
                     socketio: bool = False) -> None:
        
        if socketio:
            from .transport import SocketIOBridge

            self.bridge = SocketIOBridge(host=host, port=port)
        else:
            from .transport import BridgeServer

            self.bridge = BridgeServer(host=host, port=port)
        self.bridge.start()

    def push(self, component: Component) -> None:
        if hasattr(self.root, "on_destroy") and callable(self.root.on_destroy):
            self.root.on_destroy()
        self.stack.append(component)
        self.root = component
        if hasattr(component, "on_init") and callable(component.on_init):
            component.on_init()
        self.notify_bridge()

    def pop(self) -> None:
        if len(self.stack) > 1:
            if hasattr(self.root, "on_destroy") and callable(self.root.on_destroy):
                self.root.on_destroy()
            self.stack.pop()
            self.root = self.stack[-1]
            if hasattr(self.root, "on_init") and callable(self.root.on_init):
                self.root.on_init()
            self.notify_bridge()

    class _ReloadHandler(FileSystemEventHandler):
        def __init__(self, callback: Callable[[], None]) -> None:
            super().__init__()
            self.callback = callback

        def on_modified(self, event):
            if event.src_path.endswith(".py"):
                print(f"[HotReload] Detected change in {event.src_path}")
                self.callback()

    def _start_watcher(self, path: str) -> None:
        path = os.path.abspath(path)
        handler = self._ReloadHandler(self.notify_bridge)
        observer = Observer()
        observer.schedule(handler, path, recursive=True)
        observer_thread = threading.Thread(target=observer.start, daemon=True)
        observer_thread.start()

    def on_ui_changed(self) -> None:
        print("\n--- NOTIFIKASI KE HP ---")
        print("UI Berubah! Mengirim JSON terbaru ke Bridge...")
        print(self.build())

    def handle_event(self, event_id: str, data: Any = None) -> None:
        if event_id in self.event_registry:
            callback = self.event_registry[event_id]
            if data is not None:
                callback(data)
            else:
                callback()
        else:
            print(f"Error: Event ID {event_id} tidak ditemukan.")