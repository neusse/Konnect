# Architecture

Konnect is organized around clear runtime boundaries: the outer binary owns
process concerns, `konnect-core` owns MCP/tool behavior, and the lower crates
own specific KiCad data access strategies.

## Crate Responsibilities

### `crates/konnect`

The `konnect` crate builds the main server binary and the KiCad plugin-facing
library entry points.

Important modules:

- `src/main.rs` classifies CLI invocations, runs installer/status/transaction
  subcommands, detects double-click install mode, loads config, starts tracing,
  builds `McpHandler`, and selects the transport.
- `src/config.rs` loads TOML or JSON config from the working directory, paths
  near the executable, or the platform config directory. `KICAD_API_SOCKET`
  fills a blank `ipc_address`.
- `src/transport/stdio.rs` runs JSON-RPC over stdin/stdout. Stdout is protocol
  only; tracing goes to stderr.
- `src/transport/http.rs` runs Streamable HTTP on `/mcp` with SSE for
  server-initiated notifications and localhost-only Origin validation.
- `src/install.rs` installs bundled skills and agents for supported AI clients.
- `src/transaction_cli.rs` inspects, recovers, or force-abandons schematic
  write-ahead journals.

### `crates/konnect-core`

`konnect-core` contains the MCP protocol handler, router, observability, and all
domain tool implementations.

Important modules:

- `src/mcp/protocol.rs` defines the JSON-RPC and MCP wire types.
- `src/mcp/handler.rs` handles MCP methods, dispatches tool calls, validates
  required arguments before handlers run, emits `tools/list_changed`, and
  records observability data.
- `src/router/mod.rs` tracks loaded toolsets and maps tool names to handlers.
- `src/router/registry.rs` declares all toolsets, tool counts, descriptions, and
  the startup `STARTER_KIT`.
- `src/router/meta_tools.rs` defines always-visible router/observability tools.
- `src/tools/mod.rs` defines `ToolDef`, `ToolContext`, `ServerConfig`, the
  `tool!` macro, argument helpers, and shared KiCad path/library helpers.
- `src/tools/*.rs` are the domain toolsets: project, schematic, PCB, library,
  integration, verification, review, templates, and manufacturing.

### `crates/konnect-sexp`

`konnect-sexp` is the low-level S-expression layer used for KiCad files. It is
the right place for parsing, writing, reversible edit commands, geometry helpers,
net/layer primitives, and multi-file transaction journals.

This crate intentionally avoids requiring a live KiCad process. It is used when
Konnect needs direct file edits with atomic replacement and conflict detection.

### `crates/konnect-schematic-editor`

`konnect-schematic-editor` is the typed schematic model. Use it when a schematic
operation is easier to express as parse -> mutate typed model -> write instead
of direct S-expression edits.

It owns typed concepts such as symbols, wires, labels, sheets, and library
lookup.

### `crates/konnect-ipc`

`konnect-ipc` is the KiCad 10 IPC client. It generates Rust protobuf types from
the copied KiCad proto files, sends requests over NNG, and exposes typed helper
methods for board operations.

This crate is responsible for KiCad IPC transport classification. A transport
that cannot be reached is different from a request that reached KiCad and was
rejected or timed out. Callers use that distinction to decide whether a
file-based fallback is safe.

### `crates/schematic-viewer`

The schematic viewer is a separate Tauri application, excluded from the Cargo
workspace. It watches schematic files, renders snapshots through `kicad-cli`,
and presents a pan/zoom SVG view with multi-sheet navigation.

Because it is outside the workspace, `cargo test --workspace` does not test it.
Run its checks explicitly from `crates/schematic-viewer`.

## Non-Rust Boundaries

### `plugin`

The Python plugin is a thin KiCad integration layer. It gives users an ActionPlugin
entry in the PCB editor, displays settings, and launches/configures the Rust
server binary packaged with the PCM bundle.

### `packaging`

The packaging directory contains KiCad Plugin and Content Manager metadata,
schema validation, icon resources, and platform package scripts.

### Bundled guidance

`crates/konnect/assets/skills` and `crates/konnect/assets/agents` are distributed
with the server and installed by `konnect init` for supported AI clients. These
files are part of the user-facing AI workflow and should be kept in sync with
tool behavior.

## Ownership Rules

- Process lifecycle, CLI behavior, transport selection, and config loading belong
  in `crates/konnect`.
- MCP method handling, routing, structured tool errors, and observability belong
  in `crates/konnect-core`.
- KiCad schematic file primitives and atomic writes belong in `konnect-sexp` or
  `konnect-schematic-editor`.
- KiCad live PCB IPC behavior belongs in `konnect-ipc`.
- KiCad Plugin Manager packaging belongs in `packaging` and `plugin`.

