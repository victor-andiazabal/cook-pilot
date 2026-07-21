"""
Cook Pilot — AI cooking assistant (mini research project).

Architecture, as in the lecture slides:
    User -> UI (web environment, hosted locally) -> Backend (Python) -> OpenAI API

The backend receives the images/text from the UI, builds the request,
calls OpenAI using an API key from the OPENAI_API_KEY environment
variable (same setup as the lecture examples), and returns the result
to the UI.
"""

import os

from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="static")

# Reads OPENAI_API_KEY from the environment, exactly like the slides:
#   $env:OPENAI_API_KEY="your_api_key_here"   (Windows PowerShell)
#   export OPENAI_API_KEY="your_api_key_here" (Mac / Linux)
client = OpenAI()

# gpt-4o-mini: cheap, fast, and supports vision (needed for fridge photos).
MODEL = os.environ.get("LARDER_MODEL", "gpt-4o-mini")


def to_openai_content(blocks):
    """Convert the UI's content blocks into the OpenAI chat format.

    The UI sends a list of blocks:
      {"type": "text", "text": "..."}
      {"type": "image", "source": {"media_type": "image/jpeg", "data": "<base64>"}}
    """
    out = []
    for block in blocks:
        kind = block.get("type")
        if kind == "text":
            out.append({"type": "text", "text": block.get("text", "")})
        elif kind == "image":
            source = block.get("source", {})
            data_url = "data:{};base64,{}".format(
                source.get("media_type", "image/jpeg"),
                source.get("data", ""),
            )
            out.append({"type": "image_url", "image_url": {"url": data_url}})
    return out


@app.route("/")
def index():
    """Serve the UI (single-page web app)."""
    return send_from_directory("static", "index.html")


@app.post("/api/chat")
def chat():
    """Take content from the UI, call OpenAI, return the model's text."""
    payload = request.get_json(force=True)
    blocks = payload.get("content", [])
    if not blocks:
        return jsonify({"error": "No content provided."}), 400

    try:
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1000,
            temperature=0.7,
            messages=[{"role": "user", "content": to_openai_content(blocks)}],
        )
        text = response.choices[0].message.content or ""
        return jsonify({"text": text})
    except Exception as exc:  # surface API problems to the UI cleanly
        return jsonify({"error": str(exc)}), 502


if __name__ == "__main__":
    # Port 5001: on macOS, port 5000 is already taken by the AirPlay
    # Receiver, which answers "403 Access Denied" instead of our app.
    app.run(host="127.0.0.1", port=5001, debug=True)
