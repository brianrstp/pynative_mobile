import io
import sys
import unittest

from pynative_mobile.base import Component, PROP_UPDATE_LISTENERS
from pynative_mobile.engine import PyNativeApp
from pynative_mobile.state import State
from pynative_mobile.widgets import Button, Text, TextInput, Form
from pynative_mobile.network import fetch
from pynative_mobile.ai import generate_ui

class Dummy(Component):
    pass

class CoreTests(unittest.TestCase):
    def test_state_bind_and_unbind(self):
        s = State(10)
        called = []

        def listener(val):
            called.append(val)

        unbind = s.bind(listener)
        s.value = 20
        self.assertEqual(called, [20])
        unbind()
        s.value = 30
        self.assertEqual(called, [20])

    def test_component_serialization_and_props(self):
        s = State("hello")
        c = Dummy(text=s)
        self.assertEqual(c.props["text"], "hello")
        s.value = "world"
        self.assertEqual(c.props["text"], "world")
        d = c.to_dict()
        self.assertIn("id", d)
        self.assertEqual(d["props"]["text"], "world")

    def test_event_registry_per_app(self):
        btn = Button(label="ok")
        app1 = PyNativeApp(root=btn)
        app2 = PyNativeApp(root=btn)
        self.assertIsNot(app1.event_registry, app2.event_registry)

    def test_button_event_through_app(self):
        triggered = []

        def onpress():
            triggered.append(True)

        btn = Button(label="hit", on_press=onpress)
        app = PyNativeApp(root=btn)
        self.assertEqual(len(app.event_registry), 1)
        event_id = list(app.event_registry.keys())[0]
        app.handle_event(event_id)
        self.assertEqual(triggered, [True])

    def test_prop_update_listener_notifies_engine(self):
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            s = State(1)
            c = Dummy(count=s)
            app = PyNativeApp(root=c)
            s.value = 2
            out = buf.getvalue()
            self.assertIn("Sinyal Perubahan", out)
        finally:
            sys.stdout = old

    def test_navigation_stack(self):
        screen1 = Dummy()
        screen2 = Dummy()
        app = PyNativeApp(root=screen1)
        self.assertIs(app.root, screen1)
        app.push(screen2)
        self.assertIs(app.root, screen2)
        app.pop()
        self.assertIs(app.root, screen1)

    def test_asset_manager_inlines_image(self):
        import tempfile
        tmp = tempfile.NamedTemporaryFile(delete=False)
        tmp.write(b"hello")
        tmp.flush()
        tmp.close()

        img = Button(label="x", on_press=None)
        comp = Dummy(src=tmp.name)
        app = PyNativeApp(root=comp)
        built = app.build()
        self.assertIn("data:;base64", built)

    def test_storage_persistence(self):
        app = PyNativeApp(root=Dummy())
        app.storage.save("foo", {"bar": 1})
        self.assertEqual(app.storage.load("foo"), {"bar": 1})
        app.storage.delete("foo")
        self.assertIsNone(app.storage.load("foo"))

    def test_diffing_patch(self):
        comp = Dummy(text="a", key="x")
        app = PyNativeApp(root=comp)
        old = app.get_tree()
        comp.props["text"] = "b"
        new = app.get_tree()
        patches = app._diff_trees(old, new)
        self.assertEqual(len(patches), 1)
        self.assertEqual(patches[0]["action"], "update")
        self.assertEqual(patches[0]["prop"], "text")

        comp = Dummy(text="c")
        app = PyNativeApp(root=comp)
        old = app.get_tree()
        del comp.props["text"]
        new = app.get_tree()
        patches = app._diff_trees(old, new)
        self.assertEqual(patches[0]["action"], "remove_prop")

    def test_ai_generate_ui(self):
        screen = generate_ui("login page")
        self.assertEqual(screen.type, "Screen")

    def test_form_validation(self):
        ti1 = TextInput(name="email", value="foo@bar")
        ti2 = TextInput(name="pw", value="123")
        def email_validator(v):
            return "bad" if "@" not in v else None
        def pw_validator(v):
            return "short" if len(v) < 4 else None
        form = Form(children=[ti1, ti2], validators={"email": email_validator, "pw": pw_validator})
        errs = form.validate()
        self.assertIn("pw", errs)
        ti2.props["value"] = "1234"
        self.assertEqual(form.validate(), {})
        ti2.props["value"] = "12"
        self.assertTrue("pw" in form.validate())

    def test_lifecycle_hooks(self):
        called = []
        def init_fn():
            called.append("init")
        def destroy_fn():
            called.append("destroy")
        s1 = Dummy(on_init=init_fn, on_destroy=destroy_fn)
        s2 = Dummy()
        app = PyNativeApp(root=s1)
        app.push(s2)
        app.pop()
        self.assertEqual(called, ["destroy", "init"])

    def test_middleware_and_store(self):
        app = PyNativeApp(root=Dummy())
        def mw(a):
            a.store['called'] = True
        app.use_middleware(mw)
        app.notify_bridge()
        self.assertTrue(app.store.get('called', False))

    def test_hardware_request_and_response(self):
        app = PyNativeApp(root=Dummy())
        state = app.hardware.request_permission("camera")
        self.assertTrue(any(k.startswith("hardware_permission_") for k in app.event_registry))
        eid = [k for k in app.event_registry if k.startswith("hardware_permission_")][0]
        app.handle_event(eid, data=True)
        self.assertEqual(state.value, True)

    def test_network_fetch_mock(self):
        import httpx
        class DummyResp:
            def __init__(self, data):
                self._data = data
            def raise_for_status(self):
                pass
            def json(self):
                return self._data
        class DummyClient:
            async def __aenter__(self):
                return self
            async def __aexit__(self, exc_type, exc, tb):
                pass
            async def get(self, url):
                return DummyResp({"hello": "world"})
        orig = httpx.AsyncClient
        httpx.AsyncClient = DummyClient
        try:
            state = fetch("http://example")
            import asyncio
            asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.1))
            self.assertEqual(state.value, {"hello": "world"})
        finally:
            httpx.AsyncClient = orig

if __name__ == "__main__":
    unittest.main()