#!/usr/bin/env bash
set -euo pipefail

HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
PROVIDER_DIR="$HERMES_HOME/plugins/model-providers/nemotron-local"
PLUGIN_DIR="$HERMES_HOME/plugins/icarus_nemotron"
SKILL_DIR="$HERMES_HOME/skills/nemotron-discipline"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Installing icarus-nemotron..."

# 1. Model provider profile
mkdir -p "$PROVIDER_DIR"
cp "$SCRIPT_DIR/provider/__init__.py" "$SCRIPT_DIR/provider/plugin.yaml" "$PROVIDER_DIR/"
echo "  provider -> $PROVIDER_DIR"

# 2. Memory + tuning plugin
mkdir -p "$PLUGIN_DIR"
cp "$SCRIPT_DIR"/plugin/*.py "$SCRIPT_DIR/plugin/plugin.yaml" "$PLUGIN_DIR/"
echo "  plugin   -> $PLUGIN_DIR"

# 3. Priming skill
mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/skill/SKILL.md" "$SKILL_DIR/SKILL.md"
echo "  skill    -> $SKILL_DIR"

echo ""
echo "Done. Next:"
echo "  1. Serve Nemotron on your GPU:  scripts/serve-nemotron.sh"
echo "  2. If the model is remote, tunnel its port to localhost:"
echo "       ssh -i ~/.ssh/runpod_ed25519 -L 8000:localhost:8000 <pod> -N"
echo "  3. Point Hermes at it in ~/.hermes/config.yaml:"
echo "       model:"
echo "         provider: nemotron-local"
echo "         default: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16"
echo "  4. Restart Hermes."
