# Mobile Shell Example

This folder contains guidance for building a simple mobile "shell" application
that connects to a PyNative bridge and renders UI based on the JSON payload.

---

## Flutter Shell (Android/iOS)

Below is a minimal Flutter widget that connects to a WebSocket server and
parses incoming JSON to display corresponding widgets.  This is only a
starting point – you will need to expand it to cover all component types,
apply styling, handle events, and implement hardware plugin responses.

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

class PyNativeShell extends StatefulWidget {
  final String url;
  const PyNativeShell(this.url, {Key? key}) : super(key: key);

  @override
  _PyNativeShellState createState() => _PyNativeShellState();
}

class _PyNativeShellState extends State<PyNativeShell> {
  late WebSocketChannel channel;
  Map<String, dynamic>? tree;

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse(widget.url));
    channel.stream.listen((message) {
      final data = json.decode(message);
      if (data['tree'] != null) {
        setState(() {
          tree = data['tree'];
        });
      } else if (data['patches'] != null) {
        // apply patch logic here
      }
    });
  }

  Widget buildNode(Map<String, dynamic> node) {
    switch (node['type']) {
      case 'Text':
        return Text(node['props']['value'] ?? '');
      case 'Button':
        return ElevatedButton(
          onPressed: () {
            // send event back to Python via HTTP or WebSocket
          },
          child: Text(node['props']['label'] ?? ''),
        );
      default:
        return Container();
    }
  }

  @override
  Widget build(BuildContext context) {
    if (tree == null) return const CircularProgressIndicator();
    return buildNode(tree!);
  }
}
```

### Handling Hardware Requests
On the mobile side, listen for messages of type `"hardware"` and perform
the requested action (camera, location, etc.).  Then send an event back to
the Python engine with the response ID so that the corresponding `State` is
updated.

### Packaging
Once your shell is working, build an APK/AAB for Android or IPA for iOS using
standard Flutter tooling.

---

## React Native Shell (Optional)

A similar approach can be used with React Native and a websocket library.
React Native offers easier JavaScript-based rendering if you prefer not to
use Flutter.

---

## Preparing for Release

1. **Publish Python package**: run `python -m build` or `pip install .` and
   push to PyPI. Ensure `pyproject.toml` and `README.md` are accurate.
2. **Mobile shell distribution**: build binaries from your chosen framework
   and provide installation instructions or a storefront listing.
3. **Versioning & Changelog**: bump `version` in ``pyproject.toml`` and
   maintain a `CHANGELOG.md`.
4. **License & attribution**: include `LICENSE` file (MIT) in both Python
   package and mobile shell repos.
5. **Examples & docs**: add the shell example to repository or a separate
   repo for developers to clone.

With these pieces in place, the library is ready for external users
and contributors. Happy building!