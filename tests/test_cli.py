import os
import sys
import tempfile
import textwrap
import unittest

from pynative_mobile.cli import load_app
from pynative_mobile.engine import PyNativeApp

class Dummy(PyNativeApp):
    pass

class CLITests(unittest.TestCase):
    def test_preview_missing(self):
        from pynative_mobile.cli import main
        import webbrowser
        orig_open = webbrowser.open
        webbrowser.open = lambda url: None
        sys_argv = sys.argv
        try:
            sys.argv = ["pynative", "preview", "--file", "nope.html"]
            main()
        finally:
            webbrowser.open = orig_open
            sys.argv = sys_argv

    def test_doctor_command(self):
        from pynative_mobile.cli import main
        sys_argv = sys.argv
        try:
            sys.argv = ["pynative", "doctor"]
            import io
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            main()
            out = buf.getvalue()
            self.assertIn("Checking PyNative environment", out)
        finally:
            sys.stdout = old
            sys.argv = sys_argv

    def test_load_app_success(self):
        code = textwrap.dedent(
        )
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tf:
            tf.write(code)
            path = tf.name
        try:
            app = load_app(path)
            self.assertIsInstance(app, PyNativeApp)
        finally:
            os.unlink(path)

    def test_load_app_not_found(self):
        with self.assertRaises(FileNotFoundError):
            load_app("no_such_file.py")

    def test_new_command_creates_main(self):
        import tempfile
        tmpdir = tempfile.mkdtemp()
        from pynative_mobile.cli import main
        sys_argv = sys.argv
        try:
            sys.argv = ["pynative", "new", tmpdir]
            main()
            self.assertTrue(os.path.isfile(os.path.join(tmpdir, "main.py")))
        finally:
            sys.argv = sys_argv

