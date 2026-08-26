# Discussion Draft: Developer Documentation Map For Konnect

## Proposed category

Discussion, not incident.

This is a project-structure and maintainer-alignment topic. It is not reporting
an outage, regression, security issue, or urgent user-impacting failure. If
maintainers prefer issue-first tracking for non-trivial work, this Discussion can
be converted into or followed by a focused issue before a PR is opened.

## Title

Create a proper developer documentation set for Konnect architecture and tool
development

## Body

Konnect has useful user-facing and contributor docs today, especially `README.md`,
`DEV.md`, `CONTRIBUTING.md`, and `tool-directory.md`. The missing piece is a
navigable developer documentation set that explains how the system is composed,
how runtime flows move through the crates, and how contributors should safely
extend the tool surface.

The current docs contain many facts, but they are concentrated in a few large
files and mixed with operational notes. A new contributor still has to infer the
component model from source:

- how `crates/konnect`, `konnect-core`, `konnect-sexp`,
  `konnect-schematic-editor`, `konnect-ipc`, `schematic-viewer`, `plugin`, and
  `packaging` relate;
- how MCP startup, `tools/list`, `load_toolset`, `tools/call`, notifications,
  and observability interact;
- when a tool should use schematic file editing, KiCad IPC, or `kicad-cli`;
- what the router/toolset/schema/error contracts are;
- what tests and docs must change when a tool is added, removed, or renamed.

I propose adding a small developer-doc set:

- `docs/DEVELOPER_OVERVIEW.md` - entry point and reading order.
- `docs/ARCHITECTURE.md` - crate and directory responsibilities.
- `docs/RUNTIME_FLOWS.md` - startup, tool listing/loading, tool calls,
  schematic edits, PCB IPC edits, exports, and transaction recovery.
- `docs/TOOL_SYSTEM.md` - tool definitions, toolsets, meta-tools, dispatch,
  argument validation, structured errors, and tool-doc update rules.
- `docs/DEVELOPING_TOOLS.md` - practical checklist for adding or changing a
  tool safely.
- `docs/KICAD_INTEGRATION.md` - schematic file editing, KiCad 10 IPC,
  `kicad-cli`, config, plugin packaging, and viewer integration.
- `docs/TESTING_AND_RELEASE.md` - local checks, CI coverage, viewer/plugin/PCM
  validation, and documentation update expectations.

The intent is not to rewrite all existing documentation or create a competing
source of truth. `README.md` should stay user-facing. `DEV.md` is already a dense
internal reference and can remain authoritative for detailed implementation notes.
The proposed docs should act as the map and task guides: where to start, which
component owns what, how common runtime flows move through the system, and what a
contributor should check before changing tool behavior.

That means the PR should avoid copying drift-prone detail out of `DEV.md`, such
as exact tool totals, long error tables, or exhaustive observability fields,
unless the new page is intentionally linking back to the deeper reference. The
new files would make the architecture reviewable, reduce onboarding cost, and
give future PRs stable places to document changes without bloating `DEV.md`
further.

Questions for maintainers:

1. Is this the right documentation shape, or should some files be merged before
   the PR?
2. Is the proposed split right: new docs as map/task guides, `DEV.md` as the
   deeper implementation reference?
3. Are there architecture areas that should be explicitly included before this
   becomes a PR?
4. Do you prefer this proceed from Discussion to PR directly, or should we open
   an issue first after agreeing on scope?

## Document links

The draft documents are saved as standalone files here:

[Konnect developer documentation proposal drafts](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423)

- [Developer overview](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-developer_overview-md)
- [Architecture](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-architecture-md)
- [Runtime flows](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-runtime_flows-md)
- [Tool system](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-tool_system-md)
- [Developing tools](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-developing_tools-md)
- [KiCad integration](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-kicad_integration-md)
- [Testing and release](https://gist.github.com/neusse/46cc583b80f510032ddcd62d119d9423#file-testing_and_release-md)
