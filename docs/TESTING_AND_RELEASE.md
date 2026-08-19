# Testing And Release

This document summarizes the checks developers should understand before opening
a PR.

## Core Local Checks

Run the same main checks CI expects:

```bash
cargo test --workspace --locked --lib --tests
cargo test --workspace --locked --doc
cargo clippy --workspace --locked --all-targets -- -D warnings
cargo fmt --all -- --check
```

`protoc` is required for `konnect-ipc` protobuf code generation. Some platforms
also require the protobuf well-known type files from a separate package.

## Build Checks

Build the server binary:

```bash
cargo build --release -p konnect
```

Build the schematic viewer separately:

```bash
cd crates/schematic-viewer
cargo build --release
```

The viewer is excluded from the workspace, so workspace-level cargo commands do
not cover it.

## Test Coverage Map

| Area | Where |
|------|-------|
| MCP protocol and CLI behavior | `crates/konnect/tests` and unit tests under `crates/konnect/src` |
| Router invariants | `crates/konnect-core/src/router/mod.rs` tests |
| Tool dispatch and required-argument behavior | `crates/konnect-core/src/mcp/handler.rs` tests |
| Tool handlers and shared helpers | `crates/konnect-core` tests and module unit tests |
| S-expression parsing/writing | `crates/konnect-sexp` tests |
| Typed schematic model | `crates/konnect-schematic-editor` tests |
| KiCad IPC builders/client behavior | `crates/konnect-ipc` tests |
| Live KiCad behavior | ignored tests and `.github/workflows/e2e-kicad.yml` |
| Viewer behavior | `crates/schematic-viewer` tests and CI viewer job |
| Python plugin lifecycle | `plugin/tests` and CI plugin job |
| PCM metadata | `packaging/validate-pcm.py` and packaging CI |

## CI Shape

The normal CI workflow checks the Rust workspace across supported operating
systems, formatting, clippy, docs, viewer, plugin tests, Nix build, and PCM
metadata validation.

The end-to-end KiCad workflow runs against a real KiCad install. It is not a
normal per-PR gate and is used for scheduled, manual, and release-related
validation.

## Release Packaging

Release packaging builds standalone server binaries and KiCad PCM packages. The
macOS package is universal; platform PCM packages include the matching server
binary and plugin assets.

If a change affects plugin files, metadata, installer behavior, binary layout, or
packaged assets, validate the PCM package before proposing release.

## Documentation Checks

When a change touches public behavior, update the docs in the same PR. At
minimum, check:

- README for user-facing install or workflow changes.
- DEV.md and these developer docs for architecture or contributor workflow
  changes.
- `tool-directory.md` for tool schema/listing changes.
- Bundled skills under `crates/konnect/assets/skills` for AI workflow changes.

