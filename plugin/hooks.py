"""Lifecycle hooks — inject memory on the way in, capture decisions on the way out."""

from . import memory

# Topic-overlap guard so we don't re-inject the same memories every turn.
_last_tokens: set = set()


def on_session_start(session_id="", platform="", **kwargs):
    """Seed the session with recent activity."""
    global _last_tokens
    _last_tokens = set()
    memory.session_id = session_id
    memory.exchanges = []

    recent = memory.read_recent(limit=5)
    if not recent:
        return None
    lines = ["[memory] recent activity:"]
    for e in recent:
        ts = (e.get("timestamp") or "?")[:16]
        lines.append(f"  [{ts}] {e.get('type', '?')}: {e.get('summary', '?')}")
    return {"context": "\n".join(lines)}


def pre_llm_call(session_id="", user_message="", is_first_turn=False, **kwargs):
    """Recall relevant memories when the topic shifts."""
    global _last_tokens
    if not user_message:
        return None
    tokens = memory._tokens(user_message)
    if not tokens:
        return None
    if _last_tokens and len(tokens & _last_tokens) / max(len(tokens), 1) > 0.6:
        return None
    _last_tokens = tokens

    results = memory.recall(user_message, max_results=5)
    if not results:
        return None
    lines = ["[memory] relevant to your request:"]
    for e in results:
        ts = (e.get("timestamp") or "?")[:16]
        lines.append(f"  [{ts}] {e.get('type', '?')}: {e.get('summary', '?')}")
    return {"context": "\n".join(lines)}


def post_llm_call(session_id="", user_message="", assistant_response="", platform="", **kwargs):
    """Auto-capture high-value decisions."""
    if not assistant_response:
        return
    memory.exchanges.append({
        "user": (user_message or "")[:200],
        "assistant": assistant_response[:500],
    })
    user_text = (user_message or "").strip()
    if (memory.DECISION_RE.search(assistant_response)
            and memory.OUTCOME_RE.search(assistant_response)
            and len(assistant_response) > 200
            and len(user_text) > 50):
        body = f"Task: {user_text[:300]}\n\nResult: {assistant_response[:500]}"
        summary = assistant_response[:80].replace("\n", " ")
        status = "completed" if memory.COMPLETION_RE.search(assistant_response) else ""
        memory.write_entry("decision", body, summary,
                           status=status, training_value="high", platform=platform or "cli")


def on_session_end(session_id="", platform="", completed=False, **kwargs):
    """Write a session summary if the session had substance."""
    substantive = [e for e in memory.exchanges if len(e.get("assistant", "").strip()) > 100]
    if not substantive:
        return
    first_user = next(
        (e["user"] for e in memory.exchanges if len(e.get("user", "").strip()) > 50), "")
    parts = []
    if first_user:
        parts.append(f"## Task\n{first_user}")
    parts.append(f"## Result\n{substantive[-1]['assistant'][:500]}")
    content = "\n\n".join(parts)
    summary = content[:80].replace("\n", " ")
    memory.write_entry("session", content, summary,
                       status="completed", training_value="normal", platform=platform or "cli")
