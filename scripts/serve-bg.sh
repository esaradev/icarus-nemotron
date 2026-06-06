#!/usr/bin/env bash
# Start the server detached so it survives the terminal closing. Logs to a file.
cd "$(dirname "$0")"
pkill -f 'vllm serve' 2>/dev/null || true
sleep 1
nohup bash serve-nemotron.sh > /workspace/serve.log 2>&1 &
echo "serving in background (pid $!)"
echo "watch progress:  bash $(pwd)/status.sh"
