# icarus-nemotron

> Self-memory and output tuning for **NVIDIA Nemotron** running inside a **Hermes** agent.
>
> Remember your work. Drive tools cleanly.

A Hermes plugin in the Icarus family. It does two things for a Nemotron-backed agent:

1. **Memory** — gives the agent persistent self-memory across sessions (recall past
   decisions, auto-capture new ones), using the same `~/fabric/` markdown store as Icarus.
2. **Tuning** — points Hermes at a self-hosted Nemotron correctly and cleans up the
   model's output so its reasoning scaffolding doesn't leak into responses.

## What it ships

Two pieces that install into Hermes:

- **A model provider** (`nemotron-local`) — points Hermes at a Nemotron model served by
  vLLM over an OpenAI-compatible API, with the sampling settings Nemotron reasoning
  recommends (temperature 0.6, top_p 0.95). Separate from the bundled `nvidia` (hosted NIM)
  provider, so it doesn't touch it.
- **A memory + tuning plugin** (`icarus_nemotron`) — three memory tools, four memory
  lifecycle hooks, one output-cleanup hook, and a priming skill.

```
mem_recall / mem_write / mem_search        # memory tools
on_session_start / pre_llm_call /          # inject + capture memory
  post_llm_call / on_session_end
transform_llm_output                       # strip leaked reasoning scaffolding
skill/SKILL.md                             # primes Nemotron on tool + memory discipline
```

## Install

```bash
git clone https://github.com/esaradev/icarus-nemotron.git
cd icarus-nemotron
chmod +x install.sh
./install.sh
```

This copies the provider to `~/.hermes/plugins/model-providers/nemotron-local/`, the plugin
to `~/.hermes/plugins/icarus_nemotron/`, and the skill to `~/.hermes/skills/`. No extra
dependencies — memory is stdlib plus PyYAML, already in the Hermes venv.

## Serve Nemotron

On a machine with a GPU (the model card lists VRAM needs; Nano-30B has FP8 and BF16 variants):

```bash
NEMOTRON_MODEL=nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  scripts/serve-nemotron.sh
```

That runs:

```bash
vllm serve nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16 \
  --port 8000 --max-model-len 262144 --trust-remote-code \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --reasoning-parser-plugin nano_v3_reasoning_parser.py --reasoning-parser nano_v3
```

The `nano_v3_reasoning_parser.py` plugin ships in the model's Hugging Face repo — download it
next to the serve script. Without it, vLLM serves but reasoning parsing is weaker and tool
calls are less reliable.

If the GPU is remote, forward its port to your machine so `localhost:8000` reaches it:

```bash
ssh -i ~/.ssh/id_ed25519 -L 8000:localhost:8000 <pod> -N
```

## Point Hermes at it

In `~/.hermes/config.yaml`:

```yaml
model:
  provider: nemotron-local
  default: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-BF16
```

The provider reads `NEMOTRON_BASE_URL` (default `http://localhost:8000/v1`) and
`NEMOTRON_API_KEY` (a dummy value is fine for a local vLLM). Restart Hermes.

## How the tuning actually works (and its limit)

Tool-call reliability for Nemotron comes from three things, in order of impact:

1. **The vLLM serve flags** — `--tool-call-parser qwen3_coder` and the `nano_v3` reasoning
   parser are what turn Nemotron's output into structured tool calls. This is the real lever.
2. **The provider sampling settings** — temperature 0.6 / top_p 0.95, Nemotron's recommended
   reasoning config.
3. **The priming skill** — tells the model to finish reasoning before emitting a call, call
   one tool at a time, and use the structured tool-call format.

The `transform_llm_output` hook is a **final-text safety net only**: it strips leaked
`<think>` / `<tool_call>` / control-token fragments from the user-visible response when the
server's parser misses them. It runs after the tool loop is done, so it can't re-inject a
tool call that was dropped mid-loop. It's scoped to Nemotron models and returns the original
text unchanged for any other provider.

## Memory store

Entries are markdown files under `~/fabric/` (override with `FABRIC_DIR`), one per file, with
YAML frontmatter (`id`, `agent`, `timestamp`, `type`, `summary`, `outcome`, `training_value`).
The format matches the Icarus plugin, so the two can share a fabric directory.

## License

MIT.
