import argparse
import os
import sys
import socket
import importlib.util
from typing import Optional

try:
    import qrcode
except ImportError:  
    qrcode = None 


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def load_app(path: str) -> object:
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Could not find file at {path}")
    spec = importlib.util.spec_from_file_location("pynative_main", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    if not hasattr(module, "app"):
        raise AttributeError("main.py must define an 'app' variable")
    return getattr(module, "app")


def print_qr(text: str) -> None:
    if qrcode is None:
        print(f"Scan this URL: {text}")
        return
    img = qrcode.make(text)
    try:
        img.print_ascii(tty=True)
    except Exception:
        print(f"QR: {text}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="pynative")
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run", help="run the PyNative app")
    run_parser.add_argument("path", nargs="?", default="main.py", help="location of the application file")
    run_parser.add_argument("--host", default="0.0.0.0")
    run_parser.add_argument("--port", type=int, default=8000)
    run_parser.add_argument("--socketio", action="store_true", help="use socket.io transport")
    run_parser.add_argument("--no-watch", dest="watch", action="store_false", help="disable hot-reload watcher")

    preview_parser = sub.add_parser("preview", help="open web preview page in browser")
    preview_parser.add_argument("--file", default="web_preview.html", help="path to preview HTML file")

    doctor_parser = sub.add_parser("doctor", help="check for required dependencies and environment")

    new_parser = sub.add_parser("new", help="scaffold a new PyNative project")
    new_parser.add_argument("directory", nargs="?", default=".", help="folder to create project in")

    args = parser.parse_args()
    if args.command == "run":
        app = load_app(args.path)
        print("Starting PyNative application...")
        app.start_bridge(host=args.host, port=args.port, socketio=args.socketio)
        if args.watch:
            app._start_watcher(os.path.dirname(os.path.abspath(args.path)) or ".")
        ip = get_local_ip()
        scheme = "ws" if not args.socketio else "http"
        url = f"{scheme}://{ip}:{args.port}"
        print("Bridge listening on", url)
        print_qr(url)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("Shutting down")
    elif args.command == "preview":
        import webbrowser
        path = os.path.abspath(args.file)
        if not os.path.isfile(path):
            print(f"Preview file not found: {path}")
        else:
            print(f"Opening web preview: {path}")
            webbrowser.open(f"file://{path}")

    elif args.command == "doctor":
        print("Checking PyNative environment...")
        missing = []
        for pkg in ["fastapi", "uvicorn", "watchdog", "socketio", "qrcode", "httpx"]:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)
        if missing:
            print("Missing packages:", ", ".join(missing))
            print("Please install dependencies: pip install -r requirements.txt")
        else:
            print("All required packages are installed.")

    elif args.command == "new":
        dest = os.path.abspath(args.directory)
        if not os.path.isdir(dest):
            os.makedirs(dest, exist_ok=True)
        main_py = os.path.join(dest, "main.py")
        if not os.path.exists(main_py):
            with open(main_py, "w") as f:
                f.write("from pynative_mobile import PyNativeApp, Screen, Text\n\n")
                f.write("app = PyNativeApp(root=Screen(title=\"Hello\", children=[Text(\"World\")]))\n")
            print(f"Created {main_py}")
        else:
            print(f"{main_py} already exists")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
