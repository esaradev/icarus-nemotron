"""Lean fabric memory store.

Markdown-per-entry store under ~/fabric/, frontmatter-compatible with the Icarus
plugin so the two can share a directory. Trimmed to the essentials: write, recall,
search. Recall is self-contained (token overlap + recency) — no external retriever
dependency.
"""

import json
import logging
import os
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)

FABRIC_DIR = Path(os.environ.get("FABRIC_DIR", Path.home() / "fabric"))
AGENT_NAME = os.environ.get("HERMES_AGENT_NAME", "") or "nemotron"

# Decision/outcome detection for auto-capture (mirrors Icarus).
DECISION_RE = re.compile(
    r"(?i)\b(decided|resolved|completed|fixed|deployed|shipped|reviewed|approved|rejected)\b"
)
OUTCOME_RE = re.compile(
    r"(?i)(result:|outcome:|conclusion:|because|root cause|instead of|\d+%|\d+x)"
)
COMPLETION_RE = re.compile(
    r"(?i)\b(completed|finished|done|shipped|deployed|resolved|closed|merged|fixed)\b"
)

_STOP = frozenset(
    "the a an is was are to of in for on with it and or not i you can do this that "
    "what how please help me my be as at by from".split()
)

# Per-session scratch (reset by on_session_start).
session_id = ""
exchanges: list = []


def _yaml_scalar(value):
    return json.dumps(str(value))


def _tokens(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in _STOP and len(w) > 2}


def write_entry(entry_type, content, summary, tags="", status="", outcome="",
                training_value="", platform="cli"):
    """Write a fabric entry. Returns the filepath as a string."""
    FABRIC_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    ts_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    suffix = secrets.token_hex(2)
    slug = re.sub(r"[^a-z0-9]+", "-", summary.lower().strip())[:40].strip("-")
    stem = slug or now.strftime("%Y-%m-%dT%H%MZ")
    filename = f"{AGENT_NAME}-{entry_type}-{stem}-{suffix}.md"

    sid = session_id or f"sess-{now.strftime('%Y%m%d-%H%M%S')}-{os.getpid()}"
    project_id = os.environ.get(
        "FABRIC_PROJECT_ID",
        Path.cwd().name if Path.cwd() != Path.home() else "unknown")

    lines = [
        "---",
        f"id: {_yaml_scalar(secrets.token_hex(4))}",
        f"agent: {_yaml_scalar(AGENT_NAME)}",
        f"platform: {_yaml_scalar(platform)}",
        f"timestamp: {_yaml_scalar(ts_iso)}",
        f"type: {_yaml_scalar(entry_type)}",
        f"tier: {_yaml_scalar('hot')}",
        f"summary: {_yaml_scalar(summary)}",
        f"project_id: {_yaml_scalar(project_id)}",
        f"session_id: {_yaml_scalar(sid)}",
    ]
    if tags:
        lines.append(f"tags: [{tags}]")
    if status:
        lines.append(f"status: {_yaml_scalar(status)}")
    if outcome:
        lines.append(f"outcome: {_yaml_scalar(outcome)}")
    if training_value:
        lines.append(f"training_value: {_yaml_scalar(training_value)}")
    lines += ["---", "", content]

    path = FABRIC_DIR / filename
    path.write_text("\n".join(lines), "utf-8")
    logger.info("nemotron-mem: wrote %s", filename)
    return str(path)


def _read(path, max_bytes=4000):
    try:
        return path.read_text("utf-8")[:max_bytes]
    except OSError:
        return ""


def _head(text):
    """Pull the frontmatter fields we care about out of an entry."""
    fields = {}
    for key in ("id", "agent", "type", "summary", "timestamp", "status", "outcome"):
        m = re.search(rf"^{key}: (.+)$", text, re.MULTILINE)
        if m:
            raw = m.group(1).strip()
            fields[key] = raw[1:-1] if raw.startswith('"') and raw.endswith('"') else raw
    return fields


def _entries():
    if not FABRIC_DIR.exists():
        return []
    return sorted(FABRIC_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)


def read_recent(limit=5):
    out = []
    for f in _entries():
        h = _head(_read(f, 800))
        out.append({"id": h.get("id", ""), "agent": h.get("agent", ""),
                    "timestamp": h.get("timestamp", ""), "summary": h.get("summary", ""),
                    "type": h.get("type", "")})
        if len(out) >= limit:
            break
    return out


def recall(query, max_results=5):
    """Rank entries by query-token overlap, with a small recency tiebreak."""
    files = _entries()
    if not files:
        return []
    qt = _tokens(query)
    if not qt:
        return read_recent(max_results)

    scored = []
    for rank, f in enumerate(files):
        text = _read(f)
        h = _head(text)
        # weight the summary heavily, the body lightly
        summary_tokens = _tokens(h.get("summary", ""))
        body_tokens = _tokens(text)
        score = 3 * len(qt & summary_tokens) + len(qt & body_tokens)
        if score == 0:
            continue
        # recency tiebreak: small decay by position in the mtime-sorted list
        score += max(0, 5 - rank) * 0.1
        scored.append((score, h))

    scored.sort(key=lambda s: s[0], reverse=True)
    return [{"score": round(s, 2), **h} for s, h in scored[:max_results]]


def search_entries(query, limit=10):
    """Case-insensitive substring grep across entries."""
    q = query.lower()
    results = []
    for f in _entries():
        text = _read(f)
        if q not in text.lower():
            continue
        h = _head(text)
        matches = [ln.strip() for ln in text.split("\n") if q in ln.lower()][:3]
        results.append({"file": f.name, "agent": h.get("agent", ""),
                        "summary": h.get("summary", ""), "matches": matches})
        if len(results) >= limit:
            break
    return results
