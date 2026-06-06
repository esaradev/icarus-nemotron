"""Tool handlers. Each returns a JSON string."""

import json

from . import memory


def _json(payload):
    return json.dumps(payload, default=str)


def mem_recall(args, **kwargs):
    query = (args.get("query") or "").strip()
    if not query:
        return _json({"error": "No query provided"})
    results = memory.recall(query, max_results=args.get("max_results", 5))
    return _json({"query": query, "count": len(results), "entries": results})


def mem_write(args, **kwargs):
    entry_type = (args.get("type") or "").strip()
    content = (args.get("content") or "").strip()
    summary = (args.get("summary") or "").strip()
    if not entry_type or not content or not summary:
        return _json({"error": "Need type, content, and summary"})
    tv = (args.get("training_value") or "").strip()
    if tv and tv not in ("high", "normal", "low"):
        return _json({"error": f"training_value must be high/normal/low, got '{tv}'"})
    path = memory.write_entry(
        entry_type, content, summary,
        tags=args.get("tags", ""), outcome=args.get("outcome", ""), training_value=tv,
    )
    return _json({"status": "written", "path": path})


def mem_search(args, **kwargs):
    query = (args.get("query") or "").strip()
    if not query:
        return _json({"error": "No query provided"})
    results = memory.search_entries(query, limit=args.get("limit", 10))
    return _json({"query": query, "count": len(results), "matches": results})
