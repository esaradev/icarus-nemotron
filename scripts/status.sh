#!/usr/bin/env bash
# One command to see where the server is at.
echo "=== download size (target ~60G) ==="
du -sh /workspace/hf 2>/dev/null || echo "no cache yet"
echo "=== server up? (JSON = ready) ==="
curl -s http://localhost:8000/v1/models | head -c 300 || true
echo
echo "=== last log lines ==="
tail -n 8 /workspace/serve.log 2>/dev/null || echo "no log yet"
