# Freerouting maintainer direction and recommended contribution

**Research date:** 2026-08-25  
**Konnect release:** [v0.8.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.8.0)  
**Current upstream snapshot:** `c68c745c2a26808726a477b2ef8e56e05833bdc0`

## Decision

Yes. The maintainer is directly inviting `@neusse` to own the real Freerouting
bridge.

In his newest comment on improvement-backlog Discussion #165, `@mixelpixx`
offered four remaining P0 choices, then stated that his honest preference is the
Freerouting bridge because it is the item "nobody else can do as well as you."
He also approved the design-first process and identified a v0.8.0
konnect-codex benchmark as the project's most valuable QA event. See the
[maintainer comment](https://github.com/mixelpixx/Konnect/discussions/165#discussioncomment-18149346).

The highest-impact contribution is therefore to **claim and deliver the
Freerouting bridge**, not to select one of the smaller alternatives. The roadmap
calls this the project's "single biggest capability gap" and records the design
from #253 as the agreed direction. See
[ROADMAP.md, Autorouting](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md#3-autorouting-a-real-freerouting-bridge).

The first bounded contribution should be a **design/contract clarification on
#253 (or a maintainer-approved follow-on issue)** that resolves the missing
KiCad-side API boundary described below. Starting the public `autoroute` handler
before that decision would risk recreating the same advertised-but-unusable tool
that #276 intentionally removed.

## What is already done, and what is not

- [Issue #253](https://github.com/mixelpixx/Konnect/issues/253) documented three
  separate problems: false advertising of `autoroute`, incomplete Freerouting
  discovery, and the absence of a real editor bridge.
- [PR #276](https://github.com/mixelpixx/Konnect/pull/276) closed #253 by removing
  the always-failing `autoroute` tool and improving JAR/Java discovery. It did
  **not** implement DSN export, routing, SES import, or editor refresh.
- Current `check_freerouting` reports one compatibility-oriented `available`
  value after finding a JAR and Java. It does not yet distinguish engine
  readiness from bridge readiness.
- A search of current Konnect issues and PRs found no separate open issue or PR
  implementing the bridge. There is no duplicate implementation to avoid.
- The other choices in the maintainer's comment are now less attractive:
  [#120 already has PR #330](https://github.com/mixelpixx/Konnect/pull/330),
  while #240/#241 and #189 remain important but are smaller than the roadmap's
  autorouting gap.

There is a minor process inconsistency to resolve before claiming the work:
#253 is closed, while ROADMAP.md says implementation remains open and should be
claimed on #253. The clean next move is to comment with the proposed contract and
ask the maintainer either to reopen #253 or authorize a narrowly named follow-on
implementation issue.

## The unresolved architecture boundary

The roadmap requires a standalone Freerouting JAR plus:

1. exact-board DSN export;
2. a bounded Freerouting run;
3. exact-board, atomic SES import;
4. editor refresh and evidence-based reporting.

The standalone routing portion is straightforward. Freerouting's official CLI
documents `java -jar freerouting.jar -de board.dsn -do board.ses`, supports
headless operation with `--gui.enabled=false`, and provides controls for passes,
threads, ignored netclasses, logging, and user-data placement. See the official
[Freerouting CLI documentation](https://github.com/freerouting/freerouting/blob/master/docs/command_line_arguments.md).

The editor portion is not currently a supported KiCad IPC operation:

- KiCad 10's official `editor_commands.proto` contains document, item, commit,
  save-to-string, refresh, and `RunAction` operations, but no Specctra DSN export
  or SES import command. Konnect's vendored schema matches this boundary. See
  [KiCad 10 editor commands](https://gitlab.com/kicad/code/kicad/-/blob/10.0/api/proto/common/commands/editor_commands.proto).
- Current KiCad master still exposes no DSN/SES IPC command. See
  [current editor commands](https://gitlab.com/kicad/code/kicad/-/blob/master/api/proto/common/commands/editor_commands.proto)
  and [current board commands](https://gitlab.com/kicad/code/kicad/-/blob/master/api/proto/board/board_commands.proto).
- `RunAction` is explicitly documented by KiCad as a low-level prototyping
  facility whose action names are not an API and may change or disappear. It
  also carries only an action name, not an output/input path. It cannot form a
  stable, unattended export/import contract.
- Freerouting 2.3.0's production KiCad DSN integration calls legacy
  `pcbnew.ExportSpecctraDSN` and `pcbnew.ImportSpecctraSES`, then `pcbnew.Refresh`.
  See the official
  [`router_dsn.py`](https://github.com/freerouting/freerouting/blob/v2.3.0/integrations/KiCad/kicad-freerouting/plugins/router_dsn.py).
  That proves the workflow, but it uses the SWIG/Python API that Konnect issue
  [#257](https://github.com/mixelpixx/Konnect/issues/257) records as removed in
  KiCad 11.
- KiCad's native implementation is substantial and board-aware: the current
  source has dedicated
  [`specctra_export.cpp`](https://gitlab.com/kicad/code/kicad/-/blob/master/pcbnew/specctra_import_export/specctra_export.cpp)
  and
  [`specctra_import.cpp`](https://gitlab.com/kicad/code/kicad/-/blob/master/pcbnew/specctra_import_export/specctra_import.cpp).
  Reimplementing those semantics in Konnect would duplicate KiCad's writer,
  importer, netclass handling, pad/via conversion, and future compatibility
  work.

This means that "use the native editor bridge through IPC" and "ship the bridge
today" are not yet simultaneously achievable without one additional design
choice.

## Recommended architecture decision

Prefer a **supported Specctra operation in KiCad's IPC API**, contributed
upstream if necessary, followed by the Rust Konnect orchestration.

The KiCad side can expose existing native operations rather than recreate the
format:

- export the explicitly identified open board through KiCad's existing
  `DSN::ExportBoardToSpecctraFile` path;
- import through the existing `DSN::ImportSpecctraSession` path inside a KiCad
  commit/undo boundary;
- return structured success/failure and refresh the editor;
- support both GUI-connected KiCad 10 and KiCad 11's forward IPC architecture
  where the underlying operation is available.

This is the best fit for Konnect's Rust/IPC-only direction and for the user's
requirement that normal KiCad behavior, current netclasses, and future KiCad
fixes remain authoritative. It also benefits Freerouting's own KiCad 11
migration rather than creating a Konnect-only file-format fork.

The design-first comment should ask the maintainer to approve this two-repository
sequence or explicitly choose a temporary alternative. The alternatives all
carry worse costs:

- **Legacy SWIG ActionPlugin bridge:** proven on KiCad 10, but Python-based and
  removed by KiCad 11; inappropriate as Konnect's new stable contract.
- **`RunAction` or GUI automation:** unstable, cannot safely pass artifact paths,
  and conflicts with the roadmap's fail-closed requirements.
- **Direct Rust DSN/SES implementation:** possible, but large and duplicative;
  it must independently match KiCad's native handling and be revalidated for
  every KiCad major release.
- **Freerouting JSON/REST integration:** promising and pure Rust on the Konnect
  side, but currently experimental, changes the roadmap's agreed DSN/SES
  contract, and is exposed to Freerouting's announced pre-2.4 refactor. It is a
  future alternative only after explicit design agreement.

## Focused contribution sequence

Konnect's [CONTRIBUTING.md](https://github.com/mixelpixx/Konnect/blob/main/CONTRIBUTING.md)
requires design agreement for non-trivial work and one reviewable outcome per
PR. A safe sequence is:

### 0. Claim and settle the bridge contract

Comment on #253 with the IPC gap, request reopen/follow-on authorization, and
agree on the KiCad-upstream IPC path versus an explicitly temporary adapter.
Define the public states and rollback contract before adding a public tool.

### 1. Make capability reporting truthful

Extend Freerouting discovery without breaking the existing `available` field:

- `engine_found` and engine provenance;
- `java_ready` and version evidence;
- `bridge_ready`, bridge type, supported KiCad version, and reason when absent;
- `end_to_end_ready`, derived only when all required layers are proven.

This PR must not restore `autoroute` yet.

### 2. Add the supported exact-board export adapter

- Require the exact requested `.kicad_pcb` to be open and active.
- Save or snapshot the live board before export.
- Export a unique DSN artifact through the agreed supported bridge.
- Record board identity, revision evidence, artifact path, size, and SHA-256.
- Refuse on ambiguous board identity, lost IPC, missing export, or empty output.

[Issue #256](https://github.com/mixelpixx/Konnect/issues/256) is relevant to
opening and activating an exact board. It need not block routing an already-open
board, but it blocks a fully unattended "open then route" workflow.

### 3. Add a bounded standalone-JAR runner

- Use the discovered or explicitly supplied JAR; record its path/version.
- Pass arguments as an argv vector, never a shell string.
- Use a unique work directory and deterministic DSN/SES names.
- Support headless mode, timeout, cancellation, captured exit status, and
  bounded logs.
- Require a successful exit plus a non-empty, structurally valid SES whose
  design identity matches the exported DSN.
- Never import after timeout, cancellation, non-zero exit, missing/malformed
  SES, or identity mismatch.

Freerouting upstream is performing a large refactor targeted for 2026-08-30 and
asks contributors to keep changes small. Konnect should depend only on the
documented CLI contract, pin/test supported versions, and avoid Freerouting
internals. See the official [Freerouting README](https://github.com/freerouting/freerouting#readme).

### 4. Add atomic SES import and editor refresh

- Re-check exact board identity and revision immediately before import.
- Import within one KiCad undo/commit boundary.
- Roll back fully or leave the board byte-/state-identical on failure.
- Refresh the targeted editor only after a committed import.
- Refuse when the editor disappears or switches boards. The stale-session
  evidence work in [#240](https://github.com/mixelpixx/Konnect/issues/240) and
  its mock in [#241](https://github.com/mixelpixx/Konnect/issues/241) strengthen
  this path and should be reused rather than bypassed.

### 5. Restore `autoroute` only with end-to-end evidence

Expose the MCP tool, update tool counts/catalogue/docs, and update the bundled
PCB workflow skill only when the full pipeline can prove its result. Guidance
should choose the bridge when `end_to_end_ready`; otherwise it should direct the
user to the official Freerouting ActionPlugin instead of pretending Konnect can
route.

## Acceptance evidence

The implementation should not be accepted on unit tests alone.

### Automated boundary tests

- JAR discovery provenance and explicit-path precedence on Windows, Linux, and
  macOS.
- Java/JAR startup failure, timeout, cancellation, and child-process cleanup.
- Missing, empty, malformed, stale, and wrong-design SES refusal.
- Wrong open board, multiple boards, board switch, IPC loss, and stale-board
  refusal.
- Import failure leaves the board unchanged; successful import is one undoable
  commit.
- Public response fields derive from post-operation evidence, not requested
  values.

### Real KiCad/Freerouting round trip

Use a real KiCad-saved board fixture and capture:

- exact board path/identity and before/after revision;
- component, pad, net, placement, outline, and layer inventories unchanged;
- DSN and SES paths, sizes, hashes, engine/JAR version, Java version, command,
  duration, and exit status;
- imported track/via counts and remaining unrouted connections;
- zero introduced shorts;
- route widths, via sizes, clearances, and ignored/locked nets consistent with
  the board's Default and named netclasses;
- direct KiCad DRC evidence with no new unwaived violations;
- visible editor refresh and a single undo that removes the imported route.

Run at least one simple deterministic fixture and one representative complex
board from the konnect-codex benchmark. The latter is important because the
maintainer explicitly identified those live benchmarks as finding failures the
test suite missed.

## Best immediate action

Reply to the maintainer that we will take Freerouting, then post the design-first
contract on #253. The comment should lead with one question:

> Konnect's supported KiCad 10/current-master IPC schemas expose no native
> Specctra DSN export or SES import command, while `RunAction` is explicitly
> unstable and the working Freerouting plugin uses the SWIG/Python API removed
> in KiCad 11. May we treat adding the native Specctra operations to KiCad IPC
> as the first dependency, then build the bounded Rust JAR runner and atomic
> import orchestration in focused Konnect PRs?

That is a small decision point, but it determines whether the bridge becomes a
durable capability or another version-specific workaround.
