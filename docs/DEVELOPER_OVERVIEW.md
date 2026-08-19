# Developer Overview

This is the entry point for developers who need to understand how Konnect is put
together before changing it.

Konnect is a Rust MCP server and KiCad plugin support package. An AI client talks
to the `konnect` binary over MCP. The server exposes a small default tool set,
loads larger toolsets on demand, and routes tool calls into KiCad-facing
operations.

## Main Components

| Component | Path | Role |
|-----------|------|------|
| Server binary | `crates/konnect` | CLI, config loading, install/status commands, MCP transports, plugin FFI exports |
| Core tool server | `crates/konnect-core` | MCP handler, tool router, tool definitions, observability, and all domain tool logic |
| S-expression engine | `crates/konnect-sexp` | Low-level KiCad file parser/writer, atomic edits, reversible commands, transaction journals |
| Typed schematic editor | `crates/konnect-schematic-editor` | Higher-level schematic model for parse/mutate/write workflows |
| KiCad IPC client | `crates/konnect-ipc` | KiCad 10 IPC client using NNG and protobuf messages generated from copied KiCad proto files |
| Schematic viewer | `crates/schematic-viewer` | Separate Tauri app for live schematic rendering; excluded from the Cargo workspace |
| KiCad launcher plugin | `plugin` | Python ActionPlugin/settings UI installed by the KiCad Plugin and Content Manager package |
| Packaging | `packaging` | KiCad PCM metadata, schema validation, and package build scripts |

## Runtime Shape

Most calls follow this path:

```text
MCP client
  -> konnect transport (stdio or HTTP)
  -> McpHandler
  -> ToolRouter
  -> tool handler in konnect-core
  -> one of:
       - schematic file edit through konnect-schematic-editor / konnect-sexp
       - live PCB edit through konnect-ipc
       - export/check through kicad-cli
       - external integration such as JLCPCB database or Freerouting
```

The important design split is that schematic work is mostly file based, while
PCB work is mostly live-editor based. Schematic tools can operate on
`.kicad_sch` files without KiCad running. Most PCB tools require KiCad 10 with
the board open because they use KiCad's IPC API.

## What To Read Next

- [Architecture](ARCHITECTURE.md) explains the crate boundaries and ownership.
- [Runtime flows](RUNTIME_FLOWS.md) shows startup, tool listing, tool calls, and
  mutation paths step by step.
- [Tool system](TOOL_SYSTEM.md) explains the router, toolsets, meta-tools, and
  schema/argument contracts.
- [Developing tools](DEVELOPING_TOOLS.md) is the practical checklist for adding
  or changing an MCP tool.
- [KiCad integration](KICAD_INTEGRATION.md) covers IPC, `kicad-cli`, file
  editing, plugin launch, and packaging behavior.
- [Testing and release](TESTING_AND_RELEASE.md) explains local checks, CI
  coverage, live KiCad tests, and release packaging.

