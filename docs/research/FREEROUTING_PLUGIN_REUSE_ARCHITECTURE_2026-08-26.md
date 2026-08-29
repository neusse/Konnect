# Freerouting plugin reuse architecture for Konnect issue #337

Date: 2026-08-26

## Conclusion

Yes, the installed plugins materially reduce the work, but they do not remove
the central interchange work in [Konnect issue #337](https://github.com/mixelpixx/Konnect/issues/337).

The biggest newly confirmed shortcut is that the Freerouting 2.3.0 JAR contains
its own native Java MCP server. Konnect can launch that local JAR as an MCP child
over stdio and use structured session/job tools instead of inventing its own
Freerouting process protocol. That can cover job creation, local DSN upload,
settings, start, progress, cancellation/log handling, and local SES download.
It needs neither Node nor the public cloud in local mode. The official workflow
is documented in Freerouting's
[v2.3.0 MCP guide](https://github.com/freerouting/freerouting/blob/v2.3.0/docs/API/MCP.md).

What it does **not** cover is equally important: Freerouting MCP accepts an
already-created DSN and returns an SES. It has no connection to the exact live
KiCad document, no KiCad-to-DSN conversion, no SES-to-KiCad conversion, and no
KiCad transaction or revision check. Therefore issue #337 still needs:

1. the immutable KiCad IPC snapshot and deterministic Rust DSN lowering;
2. the strict Rust SES parser and manifest resolution; and
3. the revision-bound, atomic KiCad IPC apply and acceptance read-back.

The Konnect PCM package also saves work. It already installs native Rust
binaries and an executable `plugin.json` entrypoint, and Konnect already consumes
KiCad's socket and token environment. The Python files visible beside it are a
legacy settings/server-control shim, not the Konnect implementation. The bridge
belongs in the existing Rust binary; it does not require a new Python plugin.

## Four components that must not be conflated

### 1. Standalone Freerouting JAR

This is the routing engine. It can be downloaded independently and run through
the documented CLI, or it can expose Freerouting's local MCP server. The CLI
supports DSN input, SES output, bounded passes, and no-GUI operation; see the
[v2.3.0 CLI documentation](https://github.com/freerouting/freerouting/blob/v2.3.0/docs/command_line_arguments.md).

### 2. Freerouting KiCad PCM ActionPlugin

The PCM package installs the same JAR plus Python/wx workflow glue. Its default
DSN path calls `pcbnew.ExportSpecctraDSN`, runs the JAR, calls
`pcbnew.ImportSpecctraSES`, and refreshes the editor. Those calls are visible in
the official [v2.3.0 `router_dsn.py`](https://github.com/freerouting/freerouting/blob/v2.3.0/integrations/KiCad/kicad-freerouting/plugins/router_dsn.py).

The installed copy is at:

`C:\Users\georg\Documents\KiCad\10.0\3rdparty\plugins\app_freerouting_kicad-plugin`

Its `plugin.ini` points to `jar/freerouting-2.3.0.jar`. The installed JAR has
SHA-256 `065A2779A5CD14DAA746AD3CD7C5BF86C7C3BF56069AC75189428BC767F370DE`,
and its manifest records build revision
[`0291acb4e601cc2f6e6f9627557c087adfe9b4f2`](https://github.com/freerouting/freerouting/commit/0291acb4e601cc2f6e6f9627557c087adfe9b4f2).
Its archive contains `app/freerouting/api/mcp/*`, matching the native MCP
implementation documented above.

The ActionPlugin's experimental "JSON/API" mode is not KiCad protobuf IPC. Its
own README describes it as a SWIG board walk feeding Freerouting's localhost
REST API and warns that rule coverage is incomplete; see the official
[v2.3.0 KiCad integration README](https://github.com/freerouting/freerouting/blob/v2.3.0/integrations/KiCad/README.md).

### 3. Freerouting native MCP inside the JAR

This is a structured interface to the Freerouting engine, not a KiCad bridge.
For local/offline use the official guide starts the JAR with API and MCP enabled,
MCP stdio enabled, and the GUI disabled. It then uses this state machine:

`create_session -> enqueue_job -> upload_job_input_from_local_file -> update_job_settings -> start_job -> get_job_details -> download_job_output_to_local_file`

The implementation builds MCP tools from Freerouting's OpenAPI model so its REST
and MCP contracts stay synchronized; see
[`OpenApiMcpToolRegistry.java`](https://github.com/freerouting/freerouting/blob/v2.3.0/src/main/java/app/freerouting/api/mcp/OpenApiMcpToolRegistry.java).

### 4. Konnect KiCad PCM package

This is a hybrid package:

- `plugin/__init__.py` and `settings_dialog.py` are Python/wx files that provide
  the older ActionPlugin settings and start/stop UI;
- `plugin/plugin.json` declares an executable IPC action; and
- `bin/konnect.exe` and `bin/schematic-viewer.exe` are native Rust binaries.

The package layout is defined by Konnect's
[`build-pcm.ps1`](https://github.com/mixelpixx/Konnect/blob/main/packaging/build-pcm.ps1),
and the executable action is defined by
[`plugin.json`](https://github.com/mixelpixx/Konnect/blob/main/plugin/plugin.json).
KiCad's official add-on documentation confirms that executable plugins are
separate processes and that KiCad supplies `KICAD_API_SOCKET` and
`KICAD_API_TOKEN` when it launches them
([KiCad add-on developer guide](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)).

Konnect already reads those values in its Rust IPC client
([`client.rs`](https://github.com/mixelpixx/Konnect/blob/main/crates/konnect-ipc/src/client.rs))
and applies the socket fallback in Rust configuration
([`config.rs`](https://github.com/mixelpixx/Konnect/blob/main/crates/konnect/src/config.rs)).
That is the IPC bootstrap issue #337 needs.

## Exact reuse boundary

| Area | Reuse | Decision |
|---|---|---|
| Freerouting engine | Standalone JAR or the identical PCM-bundled JAR | Reuse directly; do not bundle a second engine. |
| JAR discovery | Konnect's existing PCM/PATH/explicit-path search in [`integration.rs`](https://github.com/mixelpixx/Konnect/blob/main/crates/konnect-core/src/tools/integration.rs) | Extend its result/provenance; do not rewrite it. Prefer parsing the Freerouting plugin's `plugin.ini` before a bounded filename scan. |
| Engine control | Freerouting's native local MCP state machine | Strong reuse candidate. Put it behind an engine adapter and validate tool schemas/version at startup. Keep the documented headless CLI as a simpler fallback. |
| Java discovery | Freerouting's known search order and JRE-25 requirement in [`java_utils.py`](https://github.com/freerouting/freerouting/blob/v2.3.0/integrations/KiCad/kicad-freerouting/plugins/java_utils.py) | Reuse the behavior/known cache locations in Rust, not the Python module. The PCM package does not bundle Java. |
| IPC bootstrap | Existing Konnect executable action, socket/token environment, Rust client | Reuse unchanged where possible. No second KiCad plugin is needed. |
| Settings | Existing Rust `Config`, `settings.json` discovery, and optional PCM dialog | Add authoritative Rust fields/tool arguments for JAR path, engine transport, timeout, passes, and artifact directory. Python UI may mirror them but must not be required. |
| Server lifecycle | Existing Konnect native executable/PCM lifecycle | Keep one Konnect server. Spawn the Freerouting JAR as an owned child for a route job and kill it on cancellation/timeout. |
| DSN/SES fixtures | Freerouting's official [`fixtures`](https://github.com/freerouting/freerouting/tree/v2.3.0/fixtures) and Specctra implementation/tests | Reuse as compatibility corpora with provenance. Add KiCad-produced golden fixtures for Konnect's supported profile. |
| DSN export | Python `pcbnew.ExportSpecctraDSN` | Do not reuse in production; it is SWIG/Python and cannot implement the Rust/IPC contract. Use it only as a KiCad-10 parity oracle during development if maintainers accept that test dependency. |
| SES import | Python `pcbnew.ImportSpecctraSES` and `pcbnew.Refresh` | Do not reuse in production. It lacks issue #337's manifest, source-revision validation, complete-plan refusal, atomic per-item checks, rollback, and non-overwriting result. |
| Experimental JSON/REST bridge | Python SWIG board walk plus Freerouting REST | Do not substitute it for #337. Native Freerouting MCP improves engine control, but the JSON board conversion remains incomplete and changes the agreed DSN/SES contract. |

## Why the Python ActionPlugin is not the shortcut it first appears to be

The production DSN path is useful evidence that the full user workflow works on
KiCad 10, but its safety contract differs from #337:

- it uses SWIG `pcbnew` export/import;
- it uses generic `freerouting.dsn` and `freerouting.ses` names;
- it performs a lossy sanitizer that strips selected characters from names;
- its normal process path opens Freerouting's GUI and waits for the user to
  close the Java window rather than passing `--gui.enabled=false`;
- it deletes input/output artifacts after success; and
- it does not bind the result to a captured board revision or check every
  imported item inside a Konnect-managed transaction.

Copying that workflow into a new Python shim would make the first demo shorter,
but would leave the hardest correctness work and introduce a Rust-to-Python
control protocol that must later be deleted. It would also violate #337's
explicit no-Python/no-SWIG acceptance criterion.

## Recommended implementation shape

Use the existing Konnect Rust binary and PCM distribution, with a small engine
abstraction:

```text
KiCad IPC snapshot
  -> Rust normalized routing model + manifest
  -> deterministic Rust DSN
  -> FreeroutingEngine
       -> preferred candidate: local JAR MCP child
       -> fallback: documented headless JAR CLI
  -> SES artifact
  -> strict Rust SES plan + manifest resolution
  -> one KiCad IPC transaction + read-back evidence
```

The local MCP adapter should start the discovered JAR as a private stdio child,
perform MCP initialization and `tools/list`, require the expected tool schemas,
then follow Freerouting's documented state machine. The child should be
per-job—or otherwise have explicit ownership and collision rules—because the
documented local launch also enables the HTTP API server. Disable authentication
only for the owned stdio/local process described by Freerouting; never expose an
unauthenticated network listener beyond loopback.

Keep a CLI adapter because it has fewer moving parts for a single route and is
the long-standing documented contract. A focused spike should compare both
against the installed 2.3.0 JAR. Prefer MCP if it demonstrably provides stable
structured progress, cancellation, settings, and diagnostics with acceptable
startup/port behavior. This choice changes only the engine runner; neither choice
changes the DSN/SES bridge design.

## Optional transitional path

The safe transition is an **assisted manual fallback**, not an automated legacy
bridge:

1. `check_freerouting` reports `engine_found`, engine provenance/version,
   `native_mcp_available`, `legacy_action_plugin_found`, and
   `end_to_end_bridge_available` separately.
2. Until the Rust bridge is complete, Konnect may direct a KiCad 10 user to run
   the official Freerouting ActionPlugin manually.
3. The ActionPlugin may serve as an offline parity oracle for generated DSN and
   imported SES fixtures, but it is not a runtime dependency of the final tool.

A temporary automated Python/SWIG bridge should be a separate, explicitly
time-boxed maintainer decision. It should not be presented as completion of
issue #337.

## KiCad 11 impact

KiCad states that the legacy SWIG bindings remain in KiCad 9 and 10 but are
removed in KiCad 11; the official replacement is the language-agnostic IPC API
([`kicad-python` README](https://gitlab.com/kicad/code/kicad-python/-/blob/main/README.md)).
Consequently:

- Freerouting 2.3.0's Python DSN ActionPlugin path does not provide a KiCad 11
  architecture;
- Konnect's Python settings/server-control shim also needs replacement or must
  become optional;
- Konnect's executable `plugin.json` plus native Rust IPC client is the correct
  forward path; and
- KiCad 11's headless `kicad-cli api-server` makes native IPC usable without a
  GUI, but it does not itself supply Specctra DSN export or SES import. Current
  KiCad `board_jobs.proto` still has no Specctra job
  ([current source](https://gitlab.com/kicad/code/kicad/-/blob/master/api/proto/board/board_jobs.proto)).

The current Konnect PCM metadata caps packages at `kicad_version_max: 10.99`, so
KiCad 11 support also requires a separately tested metadata/package update; see
[`packaging/metadata.json`](https://github.com/mixelpixx/Konnect/blob/main/packaging/metadata.json).

## Effect on the #337 PR plan

The five-part plan in #337 remains valid, with one refinement:

1. **Contract/model:** reuse Konnect's IPC bootstrap and extend capability output
   to distinguish engine, native MCP, legacy ActionPlugin, and bridge readiness.
2. **DSN export:** unchanged core work; use official fixtures and the KiCad 10
   ActionPlugin only as a parity oracle.
3. **SES planning:** unchanged core work; test against Freerouting-owned SES
   corpora and live outputs.
4. **Atomic IPC apply:** unchanged core work; the plugins provide no substitute.
5. **Public route workflow:** reuse existing JAR discovery and choose the
   validated local-MCP or CLI engine adapter. Do not add a second PCM plugin.

So the answer is: **the plugins and Freerouting MCP can noticeably shrink PR 5
and eliminate new packaging/bootstrap work, but PRs 2-4 remain the substantial
engineering effort.**

## Primary sources

- [Konnect issue #337](https://github.com/mixelpixx/Konnect/issues/337)
- [Konnect issue #253](https://github.com/mixelpixx/Konnect/issues/253)
- [Freerouting v2.3.0 MCP guide](https://github.com/freerouting/freerouting/blob/v2.3.0/docs/API/MCP.md)
- [Freerouting v2.3.0 CLI](https://github.com/freerouting/freerouting/blob/v2.3.0/docs/command_line_arguments.md)
- [Freerouting v2.3.0 KiCad integration](https://github.com/freerouting/freerouting/tree/v2.3.0/integrations/KiCad)
- [Freerouting v2.3.0 Specctra code](https://github.com/freerouting/freerouting/tree/v2.3.0/src/main/java/app/freerouting/io/specctra)
- [KiCad IPC add-on guide](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)
- [KiCad official IPC Python bindings README](https://gitlab.com/kicad/code/kicad-python/-/blob/main/README.md)
- [KiCad current board job messages](https://gitlab.com/kicad/code/kicad/-/blob/master/api/proto/board/board_jobs.proto)
- [Konnect PCM launcher/package sources](https://github.com/mixelpixx/Konnect/tree/main/plugin)
- [Konnect Freerouting discovery](https://github.com/mixelpixx/Konnect/blob/main/crates/konnect-core/src/tools/integration.rs)
