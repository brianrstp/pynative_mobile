# PyNative Mobile

PyNative Mobile is a lightweight, opinionated Python framework for building
reactive user interfaces that run on mobile devices (Android/iOS) – or in a web
preview while you wait for the native renderer to be implemented.  It was
designed for back‑end developers who think in Python but want to deliver
cross‑platform mobile UIs without learning Kotlin/Swift right away.

At its core the engine maintains a tree of ``Component`` objects and broadcasts
JSON diffs via a bridge (WebSocket or Socket.IO).  Clients can render the
structure using any technology capable of parsing the JSON – Flutter, React
Native, a custom Kotlin/Swift shell, or even plain HTML/JS.

---

## 🚀 Key Features

### UI & State

* **Component model** with properties, events, and reactive ``State`` objects.
* **Layouts**: ``Screen``, ``Column``, ``Row`` plus simple widgets like
  ``Text``, ``Button``, ``Image`` and form components.
* **Diffing algorithm** computes minimal patch set that is sent over the bridge
  – updates, additions, removals and prop changes (including key‑based
  children).
* **Lifecycle hooks**: ``on_init``/``on_destroy`` called when screens are
  pushed or popped.
* **Middleware & global store** allow intercepting every update and keep
  arbitrary data across components.

### Plugins & Services

* **Hardware plugin** to request permissions, open camera, or query GPS.  The
  mobile shell must translate hardware requests to native APIs and respond via
  an event callback.
* **Local storage**: simple key/value persistence backed by SQLite.
* **Networking**: async ``fetch(url)`` helper returning a ``State`` that updates
  when the JSON response arrives.  Works even without an asyncio loop.
* **Forms & validation**: ``Form`` component manages children ``TextInput``
  widgets and runs validators before submission.
* **AI‑assisted UI generation** (stub): ``generate_ui(prompt)`` produces a
  ``Screen`` from text; plug in an LLM for real behaviour.
* **Mobile shell example**: see ``shell_example/README.md`` for a minimal
  Flutter snippet and guidance on packaging your own renderer.
### Transport & Development Tools

* **BridgeServer** (FastAPI/WebSocket) and **SocketIOBridge** for realtime
  JSON broadcast.
* **Hot‑reload watcher**: file watcher triggers ``notify_bridge()`` when Python
  sources change.
* **Web preview**: ``web_preview.html`` renders component tree in the browser
  using simple JS; useful during early development.
* **CLI** with multiple commands:
  * ``run`` – start the app and bridge, show QR code
  * ``preview`` – open web preview page
  * ``doctor`` – check required Python dependencies
  * ``new`` – scaffold a directory with a starter ``main.py``

### Quality & Packaging

* Fully typed using ``typing`` annotations.
* Unit test suite (19 tests) covering core functionality.
* Ready to publish as a Python package via ``pyproject.toml`` / ``setuptools``.
* ``requirements.txt`` lists runtime dependencies.

---

## 📦 Installation

```bash
git clone <repo>
cd pynative-mobile
pip install -r requirements.txt
pip install .            # optional, installs as package
```

---

## 🧩 Quickstart

```python
# main.py
from pynative_mobile import PyNativeApp, Screen, Text

app = PyNativeApp(
    root=Screen(title="Hello", children=[Text("World")]),
    start_server=True,     # run bridge automatically
    watch_path=".",       # enable hot reload
)
```

Start the app with CLI:

```bash
python -m pynative_mobile.cli run
```

Scan the QR code with a compatible mobile shell or open
``web_preview.html`` in your browser to see the UI update live.

---

## 🛠 Example Features

### Using Store & Middleware

```python
app.store['user'] = None

# middleware logs every update
app.use_middleware(lambda a: print('patch sent', a.get_tree()))
```

### Form with Validation

```python
from pynative_mobile import Form, TextInput

def not_empty(v): return 'required' if not v else None

form = Form(
    children=[TextInput(name='email'), TextInput(name='pw')],
    validators={'email': not_empty, 'pw': lambda v: 'too short' if len(v)<4 else None},
    on_submit=lambda data: print('submitted', data)
)
```

### Hardware Request

```python
state = app.hardware.request_permission('camera')
state.bind(lambda granted: print('camera access', granted))
```

---

## 🧠 Extending & Embedding

Build your own mobile renderer by connecting to
``ws://<laptop-ip>:8000/ws`` (or Socket.IO endpoint) and handling payloads.
Support diff patches accordingly. Shells can be prototyped using Flutter,
React Native, or even plain web technology.

To add new widgets, subclass ``Component`` and override ``to_dict``.
Middleware allows cross-cutting concerns; lifecycle hooks provide screen
behaviour.

---

## 📄 Contribution & Roadmap

The project is evolving.  Future directions include:

* Complete mobile shell (Kotlin/Swift/Flutter) with plugin implementations.
* Authorization layer for bridge, secure transport, and token exchange.
* Advanced routing, global state management, async form validators.
* Real AI UI generation via LLM API with prompt templates.
* Packaging for PyPI, detailed API documentation, and community plugins.

Contributions welcome!  Open an issue or pull request on the repository.

---

## 📜 License

MIT License – see [LICENSE](LICENSE) for details.
