"""Tool schemas — what Nemotron sees when deciding to call a memory tool."""

MEM_RECALL = {
    "name": "mem_recall",
    "description": (
        "Retrieve relevant memories from past sessions before re-deriving work. "
        "Ranks stored entries by keyword overlap and recency. Call this when the "
        "user references earlier decisions, prior context, or anything you might "
        "have already worked out."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Topic, question, or keyword phrase to search for",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum entries to return (default: 5)",
            },
        },
        "required": ["query"],
    },
}

MEM_WRITE = {
    "name": "mem_write",
    "description": (
        "Record a memory entry so future sessions can recall it. Use this for "
        "decisions you made, problems you solved, and conclusions worth keeping. "
        "Keep the summary to one line; put detail in content."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "type": {
                "type": "string",
                "description": "Entry type: decision, resolution, research, note, session",
            },
            "content": {"type": "string", "description": "Full body of the entry"},
            "summary": {"type": "string", "description": "One-line human-readable title"},
            "tags": {"type": "string", "description": "Comma-separated tags (optional)"},
            "outcome": {"type": "string", "description": "Result or conclusion (optional)"},
            "training_value": {
                "type": "string",
                "enum": ["high", "normal", "low"],
                "description": "How valuable this is to keep (optional, default normal)",
            },
        },
        "required": ["type", "content", "summary"],
    },
}

MEM_SEARCH = {
    "name": "mem_search",
    "description": (
        "Keyword grep across stored memories. Use when you want exact substring "
        "matches rather than ranked relevance (e.g. a filename, error string, or id)."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Substring to search for"},
            "limit": {"type": "integer", "description": "Max matches (default: 10)"},
        },
        "required": ["query"],
    },
}
