#!/usr/bin/env bash
# Install vLLM into a venv on /workspace so it survives container restarts.
# RunPod wipes the container's system disk on restart; only /workspace persists.
set -e

VENV=/workspace/venv
if [ ! -x "$VENV/bin/python" ]; then
  echo "creating venv at $VENV ..."
  python3 -m venv "$VENV"
fi

echo "installing vllm into $VENV (slow, but persists on /workspace) ..."
"$VENV/bin/pip" install -q --upgrade pip
"$VENV/bin/pip" install -q vllm huggingface_hub
echo "done. vllm -> $VENV/bin/vllm"
