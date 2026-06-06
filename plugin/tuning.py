"""Nemotron output normalization.

Nemotron is a reasoning model. vLLM's reasoning + tool-call parsers usually strip
the scaffolding, but there are documented cases where fragments leak into the final
assistant text (dangling <think>/<tool_call> tags, qwen-style control tokens). This
is a final-text safety net: it cleans the user-visible response, scoped to Nemotron
so it never alters output from other providers.

It does NOT re-inject a missed tool call into the agent loop — by the time
transform_llm_output fires, the loop is done. Real tool-call reliability comes from
the vLLM serve flags (--tool-call-parser qwen3_coder --reasoning-parser nano_v3),
the provider sampling settings, and SKILL.md priming.
"""

import logging
import re

logger = logging.getLogger(__name__)

# Leaked reasoning / tool-call scaffolding tokens to strip from final text.
_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
_DANGLING_TAGS = re.compile(r"</?(?:think|tool_call|tool_response)>", re.IGNORECASE)
_CONTROL_TOKENS = re.compile(r"<\|[^|>]*\|>")  # qwen-style <|im_start|>, <|tool|>, etc.


def _looks_like_nemotron(model):
    return "nemotron" in (model or "").lower()


def transform_llm_output(response_text="", session_id="", model="", platform="", **kwargs):
    """Strip leaked reasoning/tool-call scaffolding from Nemotron's final text.

    Returns cleaned text only when it actually changed something, else None so the
    original response stands and other providers are untouched.
    """
    if not response_text or not _looks_like_nemotron(model):
        return None

    cleaned = _THINK_BLOCK.sub("", response_text)
    cleaned = _DANGLING_TAGS.sub("", cleaned)
    cleaned = _CONTROL_TOKENS.sub("", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()

    if cleaned == response_text.strip():
        return None
    logger.info("nemotron-tuning: cleaned leaked scaffolding from final response")
    return cleaned
