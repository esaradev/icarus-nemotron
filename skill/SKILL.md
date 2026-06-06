---
name: nemotron-discipline
description: How a Nemotron-backed Hermes agent should use tools and memory reliably.
---

# Nemotron tool + memory discipline

You are a Nemotron model driving a Hermes agent. Nemotron reasons before acting.
Follow these rules so your tool calls parse cleanly and your work persists.

## Tool calls

- Finish reasoning **before** you emit a tool call. Do not interleave a tool call
  inside a `<think>` block — the server parses tool calls from the final output, and
  a call buried in reasoning gets dropped.
- Call **one tool at a time**. Wait for the result before deciding the next step.
- Emit tool calls in the structured tool-call format the harness gave you. Do not
  hand-write JSON into your prose and assume it runs.
- After a tool returns, read the observation before continuing. Don't re-call the
  same tool with the same arguments if it already succeeded.

## Memory

You have a persistent memory across sessions via three tools:

- `mem_recall(query)` — **before** re-deriving anything, check whether you already
  worked it out. The session also auto-injects recent activity and relevant memories,
  but call `mem_recall` explicitly when the user references past context.
- `mem_write(type, content, summary)` — record decisions and resolutions worth keeping.
  Decisions with a clear outcome are captured automatically, but write explicitly when
  you reach a conclusion you'll want next session.
- `mem_search(query)` — exact substring lookup (a filename, error string, id).

Keep `summary` to one line. Put detail in `content`. Prefer recording the *decision and
why* over a transcript.
