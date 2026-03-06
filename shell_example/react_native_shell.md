# React Native Shell (Sketch)

Use `react-native init` to start a project, then add a WebSocket client. Below
is pseudocode to demonstrate.

```js
import React, {useState, useEffect} from 'react';
import {View, Text, Button} from 'react-native';
import {WebSocket} from 'ws';

export default function App() {
  const [tree, setTree] = useState(null);
  useEffect(() => {
    const ws = new WebSocket('ws://<host>:8000/ws');
    ws.onmessage = e => {
      const data = JSON.parse(e.data);
      if (data.tree) setTree(data.tree);
    };
  }, []);

  if (!tree) return null;
  // simple renderer (text/button)
  return (
    <View>{tree.props.value && <Text>{tree.props.value}</Text>}</View>
  );
}
```

Full implementation omitted; see Flutter example for structure.