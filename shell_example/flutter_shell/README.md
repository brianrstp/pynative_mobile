# Flutter Shell Example

This directory can contain a minimal Flutter project that connects to the
PyNative bridge.  Below is a skeleton `pubspec.yaml` and main dart file.

```yaml
name: pynative_shell
sdk: flutter

dependencies:
  flutter:
    sdk: flutter
  web_socket_channel: ^2.1.0
```

```dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(MyApp());

class MyApp extends StatefulWidget {
  @override
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  late WebSocketChannel channel;
  Map<String, dynamic>? tree;

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse('ws://<host>:8000/ws'));
    channel.stream.listen((message) {
      final data = json.decode(message);
      if (data['tree'] != null) {
        setState(() {
          tree = data['tree'];
        });
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
            channel.sink.add(json.encode({ 'event': node['events']['on_press']}));
          },
          child: Text(node['props']['label'] ?? ''),
        );
      default:
        return Container();
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        body: tree == null ? CircularProgressIndicator() : buildNode(tree!),
      ),
    );
  }
}
```

Customize further as needed; this is just a starting point.