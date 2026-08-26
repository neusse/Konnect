# Runtime Flows

This document traces the main paths through Konnect at runtime.

## Server Startup

```text
konnect process starts
  -> main.rs classifies args
  -> subcommand, help, version, double-click install, or server mode
  -> Config::load or Config::load_from
  -> tracing initialized on stderr
  -> McpHandler::new
  -> ToolRouter::new
  -> load starter kit or all toolsets
  -> run stdio, HTTP, or both transports
```

The default transport is stdio. HTTP is enabled through config with
`transport = "http"` or `transport = "both"`.

`McpHandler::new` loads only the `STARTER_KIT` toolsets by default. Set
`eager_toolsets = true` only for clients that cache the first `tools/list` and
do not react to `notifications/tools/list_changed`.

## Tool Listing

```text
client calls tools/list
  -> McpHandler::dispatch
  -> meta_tools::meta_tool_descriptions
  -> ToolRouter::active_tools
  -> MCP ListToolsResult
```

Meta-tools are always visible. Domain tools appear only when their toolset is
loaded, unless `eager_toolsets` has preloaded every toolset.

## Loading Toolsets

```text
client calls load_toolset(name)
  -> meta tool handler
  -> ToolRouter::load(name)
  -> loaded tool definitions inserted by tool name
  -> notifications/tools/list_changed emitted
```

The notification is delivered over SSE for HTTP clients and through a registered
stdout notification sink for stdio clients. After receiving it, a compliant MCP
client should call `tools/list` again.

If a caller invokes an unloaded tool, dispatch returns a structured
`toolset_not_loaded` error naming the toolset to load. If `auto_load_toolsets`
is enabled, dispatch loads the owner toolset and retries in the same call.

## Tool Call

```text
client calls tools/call
  -> McpHandler::execute_tool
  -> create call id and start timer
  -> dispatch_tool
  -> meta-tool or loaded domain tool
  -> required-argument schema gate
  -> handler function
  -> CallToolResult
  -> observability record
```

Every tool call is recorded in the in-memory observer. Calls are also appended
to a JSONL log path returned by `default_calls_log_path()` unless log file IO
fails, in which case the tool call still returns normally.

## Schematic File Edit

```text
schematic tool handler
  -> read .kicad_sch
  -> parse through typed schematic model or S-expression tree
  -> validate request and current file state
  -> apply mutation
  -> write by revision-aware atomic replacement
```

Schematic edits do not require KiCad to be running. Existing-file writes are
conflict-aware: if KiCad or another Konnect operation changes the source after
it was read, the operation must fail rather than overwrite.

Multi-file schematic changes use project-local `.konnect-transaction-*.json`
write-ahead journals. The journals include complete before/after file contents
and should be treated as sensitive project data.

## PCB IPC Edit

```text
PCB tool handler
  -> build KiCadIpcClient from config/env socket
  -> find or verify requested open board
  -> build protobuf request
  -> send over NNG
  -> decode KiCad response
  -> return MCP result
```

Most PCB mutations require KiCad 10 with the target board open. The IPC client
distinguishes an unreachable transport from a rejected request:

- Unreachable means no request completed a round trip. Some narrowly scoped
  handlers may choose a file-based fallback.
- Rejected or timed out means KiCad may have received the request. The handler
  must fail closed rather than editing the board file behind KiCad's back.

## Export And Check

Export, ERC, DRC, and rendering operations use `kicad-cli` subprocesses through
the core CLI wrapper. These paths depend on a valid `kicad_cli` config value or
auto-discovery from normal KiCad install locations.

## Transaction Recovery

```text
konnect transaction status <project-dir>
konnect transaction recover <project-dir>
konnect transaction abandon <project-dir> <transaction-id> --force
```

Use `status` first. It writes nothing and redacts journal contents. `recover`
completes pending transaction targets when possible. `abandon` is the explicit
escape hatch and requires `--force`; it retains evidence because the abandoned
journal contains complete schematic images.

