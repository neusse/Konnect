# Developing Tools

Use this checklist when adding or changing an MCP tool.

## Choose The Correct Backend

Use schematic file editing when the operation changes `.kicad_sch` content and
does not require live KiCad state. Prefer the typed schematic editor for model
level operations and `konnect-sexp` for lower-level file primitives, geometry,
atomic writes, and transaction support.

Use KiCad IPC when the operation changes a live PCB editor document or needs
KiCad's current board state. Do not edit a board file behind KiCad after a
request may have reached the editor.

Use `kicad-cli` for operations KiCad exposes as CLI checks or exports, such as
ERC, DRC, schematic export, board export, or rendering.

## Add The Tool

1. Find the right file under `crates/konnect-core/src/tools`.
2. Add a `tool!(...)` entry to that module's `tools()` vector.
3. Add the handler near related handlers in the same module.
4. Use the existing schema style in that toolset.
5. Read required arguments through `require_*` helpers or `get_path`.
6. Return `CallToolResult::json`, `text`, `image`, or `error_kind` as appropriate.
7. Update the tool count in `crates/konnect-core/src/router/registry.rs`.
8. Update `tool-directory.md` and any count references in README/DEV if totals
   changed.

## Handler Expectations

Handlers should validate the caller's target before mutating anything. For file
mutations, preserve unrelated file content and use the repository's atomic write
paths. For IPC mutations, verify that the requested board is the one being
operated on.

Required arguments must not be read with `unwrap_or` defaults. A required value
that is absent means the caller made an invalid request; silently substituting a
default can produce a plausible but wrong board or schematic.

When adding a KiCad write path with layers, use the fallible layer mapping helper
so unknown layer names are refused before any outbound IPC message is built.

## Error Behavior

Prefer structured errors for caller-actionable failures:

- Missing or wrong argument: `invalid_argument`
- Existing file changed under the operation: `conflict`
- Referenced path does not exist: `file_not_found`
- Tool exists but its toolset is inactive: handled by dispatch

Do not classify by matching error strings. The IPC client and path argument
helpers carry marker errors specifically so callers can downcast instead.

## Tests To Add

For a new tool, add tests at the lowest level that proves the risky behavior:

- pure parser/writer logic in `konnect-sexp`
- typed schematic mutation in `konnect-schematic-editor`
- handler behavior in `konnect-core`
- IPC message construction in `konnect-ipc`
- protocol behavior in `crates/konnect/tests`

Prefer real KiCad-produced fixtures for board and footprint parsing. Synthetic
fixtures are useful for narrow parser cases, but they can miss shapes KiCad
actually writes.

If the tool has required arguments, ensure the schema lists them. The exhaustive
dispatch test in `handler.rs` verifies that every registered tool refuses calls
that omit required schema fields.

## Compatibility

Treat MCP tool names, schema field names, CLI flags, config keys, environment
variables, and documented paths as public API. Public renames need compatibility
handling or an explicit migration note.

