# KiCad Integration

Konnect integrates with KiCad through three mechanisms: direct schematic file
editing, KiCad 10 IPC for live PCB operations, and `kicad-cli` subprocesses for
exports and checks.

## Direct Schematic Editing

Schematic tools operate on `.kicad_sch` files using Konnect's own parsers and
writers. This allows schematic work without a running KiCad process.

Key properties:

- Reads and writes KiCad S-expression files.
- Embeds required library symbol definitions into schematic files.
- Preserves UUID and instance-path behavior needed by KiCad.
- Uses revision-aware atomic replacement for existing-file writes.
- Uses write-ahead journals for multi-file schematic operations.

If a schematic file changed after it was read, the writer should report a
conflict rather than overwrite it.

## KiCad 10 IPC

PCB editor operations use KiCad 10's IPC API through `konnect-ipc`.

Transport details:

- NNG request/reply transport.
- Protobuf `ApiRequest` / `ApiResponse` envelope.
- Socket path from config or `KICAD_API_SOCKET`.
- API token from `KICAD_API_TOKEN` when KiCad launches the plugin.

Most PCB tools require KiCad running with the target board open. Some narrow
single-footprint operations can fall back to a closed board file only when IPC
transport is unreachable. A request that reached KiCad and timed out or was
rejected must not be treated as safe for a file fallback.

## `kicad-cli`

Konnect uses `kicad-cli` for operations that KiCad exposes through its command
line interface, including schematic export, board export, ERC, DRC, rendering,
and manufacturing outputs.

The CLI path comes from config or standard install-path discovery. On macOS,
users often need to point Konnect at the binary inside the KiCad app bundle.

## Config Sources

The server loads config from these places, in order:

1. `konnect.toml` in the working directory.
2. `settings.json` in the working directory.
3. `settings.json` beside the executable.
4. `settings.json` one directory above the executable.
5. Platform config path, such as `%APPDATA%\konnect\config.toml` on Windows.

An explicit `--config <path>` loads that file. JSON is selected by `.json`
extension; other extensions are parsed as TOML.

Important fields:

- `kicad_cli`
- `kicad_binary`
- `ipc_address` or legacy alias `ipc_socket_path`
- `transport`
- `http_address`
- `jlcpcb_db_path`
- `log_level`
- `auto_load_toolsets`
- `eager_toolsets`

If `ipc_address` is blank, `KICAD_API_SOCKET` can fill it.

## KiCad Plugin Package

The KiCad Plugin and Content Manager package includes:

- Python ActionPlugin files from `plugin`.
- Rust server binary under the package `bin` directory.
- PCM metadata and resources from `packaging`.

The Python plugin provides the PCB editor settings entry. The Rust binary is the
actual MCP server.

## Viewer

The schematic viewer is launched separately or through the
`open_schematic_viewer` tool. It watches the root schematic and sub-sheets,
renders SVG snapshots with `kicad-cli`, and updates the view without blocking
KiCad's own saves.

