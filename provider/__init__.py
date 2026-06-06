"""Nemotron self-host provider profile.

Points Hermes at a Nemotron model served by vLLM with an OpenAI-compatible API
(``vllm serve ... --enable-auto-tool-choice --tool-call-parser qwen3_coder``).
Separate from the bundled ``nvidia`` profile, which targets hosted NIM with
Bearer auth and a fixed cloud base_url.

Endpoint comes from NEMOTRON_BASE_URL (default http://localhost:8000/v1). For a
remote pod, SSH-forward the pod's vLLM port to localhost first:

    ssh -i ~/.ssh/id_ed25519 -L 8000:localhost:8000 <pod> -N
"""

import os

from providers import register_provider
from providers.base import ProviderProfile

# Nemotron 3 reasoning models recommend temperature 0.6 / top_p 0.95.
# top_p is not a ProviderProfile field, so it goes through build_api_kwargs_extras.
_TEMPERATURE = 0.6
_TOP_P = 0.95


class NemotronLocalProfile(ProviderProfile):
    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        # vLLM (OpenAI-compatible) reads top_p as a top-level sampling param.
        return {}, {"top_p": _TOP_P}


nemotron_local = NemotronLocalProfile(
    name="nemotron-local",
    aliases=("nemotron",),
    api_mode="chat_completions",
    display_name="Nemotron (self-hosted)",
    description="NVIDIA Nemotron served locally via vLLM",
    signup_url="https://huggingface.co/nvidia",
    env_vars=("NEMOTRON_API_KEY",),
    base_url=os.environ.get("NEMOTRON_BASE_URL", "http://localhost:8000/v1"),
    fixed_temperature=_TEMPERATURE,
    default_max_tokens=8192,
    fallback_models=("nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16",),
    # vLLM serves whatever you launch; live /models works, so health check stays on.
)

register_provider(nemotron_local)
