"""icarus-nemotron — memory + output tuning for Nemotron-backed Hermes agents.

Tools (toolset ``nemotron_mem``):
  mem_recall  — ranked retrieval from the fabric store
  mem_write   — record a memory entry
  mem_search  — keyword grep

Hooks:
  on_session_start    — inject recent activity
  pre_llm_call        — recall relevant memories on topic shift
  post_llm_call       — auto-capture high-value decisions
  on_session_end      — write a session summary
  transform_llm_output — strip leaked reasoning scaffolding from Nemotron output
"""

import logging

from . import schemas, tools, hooks, tuning

logger = logging.getLogger(__name__)


def register(ctx):
    ctx.register_tool(name="mem_recall", toolset="nemotron_mem",
                      schema=schemas.MEM_RECALL, handler=tools.mem_recall)
    ctx.register_tool(name="mem_write", toolset="nemotron_mem",
                      schema=schemas.MEM_WRITE, handler=tools.mem_write)
    ctx.register_tool(name="mem_search", toolset="nemotron_mem",
                      schema=schemas.MEM_SEARCH, handler=tools.mem_search)

    ctx.register_hook("on_session_start", hooks.on_session_start)
    ctx.register_hook("pre_llm_call", hooks.pre_llm_call)
    ctx.register_hook("post_llm_call", hooks.post_llm_call)
    ctx.register_hook("on_session_end", hooks.on_session_end)
    ctx.register_hook("transform_llm_output", tuning.transform_llm_output)

    logger.info("icarus-nemotron registered (3 tools, 5 hooks)")
