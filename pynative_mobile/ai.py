from .layouts import Screen, Column, Row
from .widgets import Text, Button

def generate_ui(prompt: str) -> Screen:
    return Screen(title="AI Generated", children=[
        Column(children=[
            Text(f"Prompt: {prompt}"),
            Button(label="OK")
        ])
    ])
