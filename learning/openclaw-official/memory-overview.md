Title:

URL Source: https://docs.openclaw.ai/concepts/memory.md

Published Time: Mon, 30 Mar 2026 01:56:46 GMT

Markdown Content:
> ## Documentation Index
> Fetch the complete documentation index at: https://docs.openclaw.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Memory Overview

# Memory Overview

OpenClaw remembers things by writing **plain Markdown files** in your agent's
workspace. The model only "remembers" what gets saved to disk -- there is no
hidden state.

## How it works

Your agent has two places to store memories:

* **`MEMORY.md`** -- long-term memory. Durable facts, preferences, and
  decisions. Loaded at the start of every DM session.
* **`memory/YYYY-MM-DD.md`** -- daily notes. Running context and observations.
  Today and yesterday's notes are loaded automatically.

These files live in the agent workspace (default `~/.openclaw/workspace`).

 If you want your agent to remember something, just ask it: "Remember that I prefer TypeScript." It will write it to the appropriate file.

## Memory tools

The agent has two tools for working with memory:

* **`memory_search`** -- finds relevant notes using semantic search, even when
  the wording differs from the original.
* **`memory_get`** -- reads a specific memory file or line range.

Both tools are provided by the active memory plugin (default: `memory-core`).

## Memory search

When an embedding provider is configured, `memory_search` uses **hybrid
search** -- combining vector similarity (semantic meaning) with keyword matching
(exact terms like IDs and code symbols). This works out of the box once you have
an API key for any supported provider.

 OpenClaw auto-detects your embedding provider from available API keys. If you have an OpenAI, Gemini, Voyage, or Mistral key configured, memory search is enabled automatically.

For details on how search works, tuning options, and provider setup, see
[Memory Search](/concepts/memory-search).

## Memory backends

  SQLite-based. Works out of the box with keyword search, vector similarity, and hybrid search. No extra dependencies.   Local-first sidecar with reranking, query expansion, and the ability to index directories outside the workspace.   AI-native cross-session memory with user modeling, semantic search, and multi-agent awareness. Plugin install.

## Automatic memory flush

Before [compaction](/concepts/compaction) summarizes your conversation, OpenClaw
runs a silent turn that reminds the agent to save important context to memory
files. This is on by default -- you do not need to configure anything.

 The memory flush prevents context loss during compaction. If your agent has important facts in the conversation that are not yet written to a file, they will be saved automatically before the summary happens.

## CLI

```bash  theme={"theme":{"light":"min-light","dark":"min-dark"}}
openclaw memory status          # Check index status and provider
openclaw memory search "query"  # Search from the command line
openclaw memory index --force   # Rebuild the index
```

## Further reading

* [Builtin Memory Engine](/concepts/memory-builtin) -- default SQLite backend
* [QMD Memory Engine](/concepts/memory-qmd) -- advanced local-first sidecar
* [Honcho Memory](/concepts/memory-honcho) -- AI-native cross-session memory
* [Memory Search](/concepts/memory-search) -- search pipeline, providers, and
  tuning
* [Memory configuration reference](/reference/memory-config) -- all config knobs
* [Compaction](/concepts/compaction) -- how compaction interacts with memory

Built with [Mintlify](https://mintlify.com).
