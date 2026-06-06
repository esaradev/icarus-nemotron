#!/usr/bin/env bash
# Serve Nemotron with vLLM on the pod, OpenAI-compatible, tool calling enabled.
# Run this ON the pod (it needs the GPU). Defaults to Nemotron-3 Nano 30B.
set -euo pipefail

MODEL="${NEMOTRON_MODEL:-nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16}"
PORT="${NEMOTRON_PORT:-8000}"
MAX_LEN="${NEMOTRON_MAX_LEN:-262144}"
PARSER_PLUGIN="${NEMOTRON_REASONING_PLUGIN:-nano_v3_reasoning_parser.py}"

# RunPod's container disk (/) is tiny (~20G); the big volume is /workspace. The
# model is tens of GB, so cache it on /workspace unless the caller set HF_HOME.
if [[ -z "${HF_HOME:-}" && -d /workspace ]]; then
  export HF_HOME=/workspace/hf
  echo "HF_HOME defaulted to $HF_HOME (model cache on the large volume)"
fi

# Prefer a persistent vLLM in /workspace/venv (survives container restarts) over
# a system-disk install that gets wiped on restart.
VLLM_BIN="vllm"
if [[ -x /workspace/venv/bin/vllm ]]; then
  VLLM_BIN=/workspace/venv/bin/vllm
fi

# The reasoning-parser plugin ships in the NVIDIA model repo. If it's not next to
# this script, fetch it from the model card before serving (see README).
if [[ ! -f "$PARSER_PLUGIN" ]]; then
  echo "WARNING: $PARSER_PLUGIN not found in $(pwd)."
  echo "Download it from the model's Hugging Face repo, or unset NEMOTRON_REASONING_PLUGIN"
  echo "to serve without reasoning parsing (tool calls may be less reliable)."
fi

exec "$VLLM_BIN" serve "$MODEL" \
  --port "$PORT" \
  --max-model-len "$MAX_LEN" \
  --trust-remote-code \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser-plugin "$PARSER_PLUGIN" \
  --reasoning-parser nano_v3
