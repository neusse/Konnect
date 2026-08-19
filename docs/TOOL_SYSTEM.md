# Tool System

Konnect's MCP API is organized as a small always-visible starter surface plus
toolsets that are loaded on demand.

## Core Types

`ToolDef` in `crates/konnect-core/src/tools/mod.rs` is the unit of exposure:

- `name`: public MCP tool name.
- `description`: text shown to the model/client.
- `input_schema`: JSON Schema object exposed in `tools/list`.
- `handler`: async function receiving JSON arguments and `ToolContext`.

The `tool!` macro builds a `ToolDef` from a name, description, schema, and typed
async handler.

`ToolContext` carries:

- `ServerConfig`
- shared `ToolRouter`
- shared `CallObserver`
- in-memory JLCPCB query cache

## Toolsets

Toolsets are declared in `crates/konnect-core/src/router/registry.rs`.

Each entry in `ALL_TOOLSETS` has:

- `name`
- `description`
- `category`
- `tool_count`

`tools_for(name)` maps a toolset name to that module's `tools()` function. The
router tests assert that the declared `tool_count` matches the actual number of
tools returned.

The default starter kit is:

```text
project
config
```

Together with meta-tools, this keeps the baseline `tools/list` small. Load larger
domains only when the current task needs them.

## Meta-Tools

Meta-tools are always visible and handled before domain tools. They include
toolset discovery/loading and observability tools such as recent-call and server
statistics queries.

Meta-tools are not part of `ALL_TOOLSETS`, so do not add them to a domain count.

## Dispatch Rules

Tool dispatch in `McpHandler` follows this order:

1. Try meta-tool.
2. Try loaded domain tool.
3. If `auto_load_toolsets` is enabled, find the owner toolset, load it, and try
   again.
4. If the tool exists but is not loaded, return structured `toolset_not_loaded`.
5. If no registered tool owns the name, return structured `unknown_tool`.

When `load_toolset` or `unload_toolset` changes the active set, the server emits
`notifications/tools/list_changed`.

## Argument Contracts

The schema `required` list is enforced at dispatch before the handler runs. This
prevents handlers from accidentally substituting defaults for omitted required
arguments.

Inside handlers, use the argument helpers in `tools/mod.rs`:

- `require_str`
- `require_f64`
- `require_array`
- `require_u64`
- `get_path`

The schema gate checks presence only. Type-specific helpers still matter because
they produce structured `invalid_argument` errors for wrong types.

An explicit empty array is a valid value. A missing array is an argument error.

## Structured Errors

MCP `CallToolResult` has no top-level structured error object. Konnect encodes
structured error details inside the text content as JSON while setting
`is_error: true`.

Current common kinds include:

- `toolset_not_loaded`
- `unknown_tool`
- `invalid_argument`
- `file_not_found`
- `conflict`
- `handler_error`

Add new error kinds in `crates/konnect-core/src/mcp/error.rs`, then use
`CallToolResult::error_kind`.

## Updating Tool Documentation

When adding, removing, or renaming tools:

1. Update the toolset module's `tools()` list.
2. Update `tool_count` in `router/registry.rs`.
3. Regenerate or update `tool-directory.md`.
4. Update README and DEV stats if total counts changed.
5. Add or update tests that cover the schema, argument validation, and failure
   path.

