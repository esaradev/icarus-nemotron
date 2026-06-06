#!/usr/bin/env bash
# Probe the served model: does Nemotron emit a clean, parseable tool call?
# Run on the pod (or anywhere that can reach the endpoint) once the server is up.
set -euo pipefail

BASE="${NEMOTRON_BASE_URL:-http://localhost:8000/v1}"
MODEL="${NEMOTRON_MODEL:-nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16}"

read -r -d '' PAYLOAD <<JSON || true
{
  "model": "$MODEL",
  "messages": [
    {"role": "user", "content": "What is the weather in Paris right now? Use the available tool."}
  ],
  "tools": [
    {"type": "function", "function": {
      "name": "get_weather",
      "description": "Get the current weather for a city",
      "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}
    }}
  ],
  "tool_choice": "auto",
  "temperature": 0.6,
  "top_p": 0.95
}
JSON

echo "POST $BASE/chat/completions"
curl -s "$BASE/chat/completions" -H "Content-Type: application/json" -d "$PAYLOAD"
echo
