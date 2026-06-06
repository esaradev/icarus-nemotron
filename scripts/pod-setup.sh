#!/usr/bin/env bash
# One-shot pod bootstrap: install vLLM, fetch Nemotron's reasoning parser, serve.
# Run on the pod (needs the GPU). First run downloads the model (~tens of GB).
set -euo pipefail

MODEL="${NEMOTRON_MODEL:-nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "[1/3] installing vllm (this takes a few minutes)..."
pip install -q --upgrade vllm huggingface_hub hf_transfer
export HF_HUB_ENABLE_HF_TRANSFER=1

echo "[2/3] fetching reasoning parser from the model repo..."
PARSER="$SCRIPT_DIR/nano_v3_reasoning_parser.py"
if [ ! -f "$PARSER" ]; then
  curl -fsSL "https://huggingface.co/${MODEL}/resolve/main/nano_v3_reasoning_parser.py" -o "$PARSER" \
    || echo "WARN: parser fetch failed; check the model card for the right filename"
fi

echo "[3/3] serving on :8000 (first run downloads the model, be patient)..."
cd "$SCRIPT_DIR"
exec bash serve-nemotron.sh
