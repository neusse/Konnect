# Konnect improvement backlog — 26-Aug-2026 (v0.9.0)

> **Disclosure.** I posted this Codex-assisted evaluation after reviewing the
> Konnect v0.9.0 release and source, the current roadmap and contributor rules,
> every open issue, every open pull request, relevant closed and merged work,
> maintainer responses, project discussions, and our actual end-to-end KiCad
> use with the version-matched `konnect-codex` plugin. The priorities below are
> recommendations, not maintainer assignments. Before implementing an item, I
> will claim it on the issue, agree on the design, and follow the roadmap and
> contribution process with focused PRs.

## Snapshot

- Released contract: [v0.9.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.9.0),
  tag commit [`8648fe25`](https://github.com/mixelpixx/Konnect/commit/8648fe2573377eac78525907cbdd16216986f08e).
- Released surface: **19 toolsets, 206 registered tools, 212 total tools**.
- Current upstream `main`: [`2b5a33f`](https://github.com/mixelpixx/Konnect/commit/2b5a33f62a087d54b670ac41a93f4d1827c1b4e9),
  already 17 substantial commits beyond the tag, with **20 toolsets, 210
  registered tools, 216 total tools**.
- Live inventory at publication: **30 open issues and eight open pull requests**.
- Companion reviewed and installed: `konnect-codex` v0.9.0 companion revision 1.

The release and current `main` are separate snapshots. Rendering, visual
baselines, design hashes, geometry scaffolding and placement scoring on current
`main` are promising, but they are not v0.9.0 features until released.

## Executive assessment

v0.9.0 is a meaningful correctness release. It adds atomic, revision-gated
footprint-library refresh; atomic batch placement with live readback; junction
reconciliation after ordinary schematic movement; multi-unit schematic
mutations; trustworthy live pad readback; transformed symbol geometry; and
correct bus-entry endpoint reporting.

The most important new limitation is
[#331](https://github.com/mixelpixx/Konnect/issues/331): the new
`update_footprints_from_library` tool correctly refuses unsupported content,
but `fp_text user` makes it refuse most official KiCad footprints. This is safe
failure, not corruption, but it prevents the advertised workflow for the
dominant library case.

The P0 group is now narrower and more actionable. #326 has a green active fix
in #333. #240 still guards against stale-file mutation after live IPC loss;
#252 still requires truthful artifact verification; #189 can choose an
unrelated project root; and #182 still has unit-1-only readers even though its
mutation half shipped.

## Released progress in v0.9.0

- [#232](https://github.com/mixelpixx/Konnect/pull/232) adds atomic,
  dry-run/revision-gated `update_footprints_from_library` and closes #231.
- [#264](https://github.com/mixelpixx/Konnect/pull/264) adds atomic
  `set_component_placements`, one undo entry and post-commit readback.
- [#330](https://github.com/mixelpixx/Konnect/pull/330) reconciles junction dots
  after ordinary component moves and closes #120. Actual wire-carrying movement
  remains #315.
- [#273](https://github.com/mixelpixx/Konnect/pull/273) makes reference-based
  mutations affect all placed units. #182 remains open for batch/export/
  analysis/review readers.
- [#265](https://github.com/mixelpixx/Konnect/pull/265) makes live pad readback
  fail instead of fabricating or dropping data.
- [#275](https://github.com/mixelpixx/Konnect/pull/275) uses transformed symbol
  geometry for layout and overlap checks.
- #329 is closed: `add_bus_entry` responses now report the endpoints actually
  written.
- Dependency PRs #243, #320 and #321 also shipped.

## P0 — correctness and non-destructive behavior

### 1. Preserve the complete Default netclass — #326 / PR #333

[#326](https://github.com/mixelpixx/Konnect/issues/326) can omit `wire_width`
from the Default netclass and cause Eeschema to suppress or strip junction
dots. [PR #333](https://github.com/mixelpixx/Konnect/pull/333) is mergeable and
green across platforms. Keep the issue at P0 until the fix is released and a
real project proves the complete field set, T-junction connectivity and ERC
survive a KiCad round trip.

### 2. Refuse stale-file mutation after live IPC loss — #240 / #241 / PR #334

[#240](https://github.com/mixelpixx/Konnect/issues/240) remains the central
wrong-state hazard: after observing a live board, Konnect must not silently
fall back to a stale file when IPC disappears. #241 supplies the reusable
document-answering mock. [PR #334](https://github.com/mixelpixx/Konnect/pull/334)
is relevant groundwork, but its platform test failures need resolution.

Every mutator should bind to the requested document identity, report its source
and fail closed when a formerly live document is unavailable.

### 3. Verify every reported artifact — #252 / PR #270

[#252](https://github.com/mixelpixx/Konnect/issues/252) requires every snapshot,
export and manufacturing response to verify the requested output path,
existence, nonzero size, format signature, board/revision identity and
per-artifact failure state. [PR #270](https://github.com/mixelpixx/Konnect/pull/270)
is still the main implementation path but now conflicts with `main` and needs a
focused rebase.

### 4. Finish unit-aware reads and analyses — #182

v0.9.0 fixes multi-unit mutation. The remaining
[#182](https://github.com/mixelpixx/Konnect/issues/182) scope is unit-1-only
behavior in `sch_batch`, `sch_export`, `sch_analysis` and `design_review`.
Complete those reads with multi-unit fixtures without reopening the solved
mutation work.

### 5. Bound project-root and library discovery — #189

[#189](https://github.com/mixelpixx/Konnect/issues/189) can still select an
unrelated ancestor project or library table. Search must stop at an explicit
project boundary, expose candidates and refuse ambiguity rather than choosing
the first match.

## P1 — high-value workflow reliability

### Footprint refresh and schematic connectivity

- [#331](https://github.com/mixelpixx/Konnect/issues/331): represent and
  preserve standard `fp_text user` content so official footprints pass
  dry-run/apply/save/no-op convergence. Never solve this by dropping artwork.
- [#328](https://github.com/mixelpixx/Konnect/issues/328): make the shared
  connectivity index understand buses, bus entries and bus-attached labels.
  Until then, KiCad ERC remains authoritative for bus sheets.
- [#315](https://github.com/mixelpixx/Konnect/issues/315): implement actual
  connected wire movement. v0.9.0 completed junction reconciliation, not wire
  stretching or shrinking.

### Lifecycle and client reachability

- [#103](https://github.com/mixelpixx/Konnect/issues/103): server-owned
  multi-instance lifecycle and orphan cleanup remain open.
- [#242](https://github.com/mixelpixx/Konnect/issues/242): MCP startup must not
  reinstall guidance after explicit uninstall.
- [#233](https://github.com/mixelpixx/Konnect/issues/233) and
  [#325](https://github.com/mixelpixx/Konnect/issues/325): support clients that
  cap tools or never refetch changed tool lists with a compact surface and/or
  MCP resource directory.

### Board identity, platform and mutation completeness

- [#256](https://github.com/mixelpixx/Konnect/issues/256): open and prove the
  exact requested board.
- [#257](https://github.com/mixelpixx/Konnect/issues/257): prepare for KiCad 11
  SWIG removal and deprecated IPC fields.
- [#254](https://github.com/mixelpixx/Konnect/issues/254): discover supported
  per-user Windows KiCad installs.
- [#258](https://github.com/mixelpixx/Konnect/issues/258): add explicit custom
  field upsert for batch schematic edits.
- [#291](https://github.com/mixelpixx/Konnect/issues/291): honor or reject the
  requested schematic SVG filename. The post-tag PNG renderer does not close it.
- [#119](https://github.com/mixelpixx/Konnect/issues/119): bound and preserve
  complete DRC output.
- [#221](https://github.com/mixelpixx/Konnect/issues/221): make live-CI claims
  real and fix rotation-readback flakiness.
- [#84](https://github.com/mixelpixx/Konnect/issues/84): finish replacing
  indentation and line-ending-sensitive scans with structural reads.

### Freerouting bridge

The maintainer explicitly identified Freerouting as the preferred contribution.
The direction remains a standalone JAR with exact-board binding, DSN export,
headless routing, atomic SES import and route acceptance evidence. Launching
Java is straightforward and needs no computer-use automation. The unresolved
architecture decision is how a Rust/IPC-only Konnect supports durable DSN
export and SES import now that the companion's KiCad 10 Python/SWIG bridge has
a KiCad 11 deadline under #257.

Because #253 is closed while the roadmap still says to claim implementation
there, agree with the maintainer whether to reopen it or create a focused
implementation issue. Then use a short PR series: capability contract; DSN
producer; SES parser and dry-run plan; atomic IPC apply; public autoroute
workflow and end-to-end evidence.

## P2/P3 — bounded enhancements and maintenance

- [#118](https://github.com/mixelpixx/Konnect/issues/118) — true layer-aware
  2-D board plot.
- [#131](https://github.com/mixelpixx/Konnect/issues/131) — sign and notarize
  both macOS slices and final artifacts. This is P1 release work.
- [#154](https://github.com/mixelpixx/Konnect/issues/154) — Homebrew after
  signed artifacts stabilize.
- [#181](https://github.com/mixelpixx/Konnect/issues/181) — preserve lock-name
  compatibility before the `sha2` upgrade.
- [#210](https://github.com/mixelpixx/Konnect/issues/210) — reduce whole-sheet
  reserialization diff churn.
- [#225](https://github.com/mixelpixx/Konnect/issues/225) — select footprint
  graphics by stable identity, not only layer.
- [#226](https://github.com/mixelpixx/Konnect/issues/226) — restore placed
  Datasheet and Description fidelity based on measured impact.
- [#296](https://github.com/mixelpixx/Konnect/issues/296) — advanced symbol and
  footprint generation as focused tool-plus-guidance PRs.
- [#305](https://github.com/mixelpixx/Konnect/issues/305) — supported placed
  footprint 3-D model editing.

## Post-release `main`: important but not released

The 17 commits after v0.9.0 add gate/verdict contracts, design hashes,
structural board geometry, `konnect-render`, `konnect-vcs`,
`render_schematic_png`, visual baseline capture/comparison and
`score_placement` in a new placement toolset. These align with the workflow
gaps documented in
[Discussion #295](https://github.com/mixelpixx/Konnect/discussions/295).

Once released, the guidance should use native schematic rendering, visual
baseline comparison and placement scoring as evidence sources rather than
duplicating those judgments. For now, feature-detect them on `main`; do not
describe them as v0.9.0 capabilities.

## Open pull-request assessment

“Conflicting” describes Git state, not code quality. Status below is from the
publication snapshot.

| PR | State | Backlog assessment |
| --- | --- | --- |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) reload server | Conflicting, stale | A POSIX `exec` is not a complete Windows or multi-instance lifecycle solution. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) nested validation | Conflicting | Reduce to coverage not already shipped through #234 work. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) artifact verification | Conflicting | Still the main #252 path; rebase and preserve a focused truth-in-artifacts scope. |
| [#322](https://github.com/mixelpixx/Konnect/pull/322) structural library fields | Mergeable, green | Strong structural replacement for escaped and multiline field reads. |
| [#332](https://github.com/mixelpixx/Konnect/pull/332) junction sheet-pin test | Mergeable, green | Useful coverage of the v0.9.0 junction reconciler. |
| [#333](https://github.com/mixelpixx/Konnect/pull/333) complete Default netclass | Mergeable, green | Active P0 #326 fix; review whether the caller-visible response refactor belongs in the same PR. |
| [#334](https://github.com/mixelpixx/Konnect/pull/334) shared IPC gate/mock | Blocked; platform tests failed/cancelled | Useful #240/#241 groundwork after the failing test is fixed. |
| [#335](https://github.com/mixelpixx/Konnect/pull/335) delete graphics | Conflicting; Ubuntu failed | Rebase and reconcile its append semantics with the already-fixed outline replacement behavior. |

## Complete open-issue disposition

| Issue | Priority | Current disposition |
| --- | --- | --- |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) | P1 | Finish structural schematic parsing in staged conversions. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) | P1 | Server ownership and multi-instance lifecycle. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) | P2 | Layer-aware 2-D board plot. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) | P1 | Bounded, complete DRC output. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) | P1 | macOS signing and notarization. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) | P2 | Homebrew after signed artifacts stabilize. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) | P3 | Preserve lock-name compatibility before dependency bump. |
| [#182](https://github.com/mixelpixx/Konnect/issues/182) | P0 | Finish unit-aware batch/export/analysis/review reads; mutation shipped. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) | P0 | Bound root/library discovery and refuse ambiguity. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) | P2 | Reduce serialization diff churn. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) | P1 | Fix live-CI claims and rotation race. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) | P2 | Select footprint graphics by identity. |
| [#226](https://github.com/mixelpixx/Konnect/issues/226) | P3 | Restore placed metadata fidelity based on evidence. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) | P1 | Support capped/non-refreshing client tool lists. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) | P0 | Refuse stale fallback after observed-live IPC loss. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) | P1 support | Shared document-answering IPC mock for #240. |
| [#242](https://github.com/mixelpixx/Konnect/issues/242) | P1 | Remove startup guidance mutation. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) | P0 | Verify every reported artifact. |
| [#254](https://github.com/mixelpixx/Konnect/issues/254) | P1 | Per-user Windows KiCad discovery. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) | P1 | Open and prove the requested PCB document. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) | P1/deadline | KiCad 11 lifecycle and SWIG removal. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) | P1 | Explicit custom-field upsert. |
| [#291](https://github.com/mixelpixx/Konnect/issues/291) | P1 | Honor or reject requested SVG filename. |
| [#296](https://github.com/mixelpixx/Konnect/issues/296) | P2 | Focused advanced symbol/footprint generation. |
| [#305](https://github.com/mixelpixx/Konnect/issues/305) | P2 | Route placed-footprint 3-D model editing. |
| [#315](https://github.com/mixelpixx/Konnect/issues/315) | P1 | Implement actual connected wire movement. |
| [#325](https://github.com/mixelpixx/Konnect/issues/325) | P1 | Compact surface/resource directory for capped clients. |
| [#326](https://github.com/mixelpixx/Konnect/issues/326) | P0, active | Preserve Default netclass; green fix in #333. |
| [#328](https://github.com/mixelpixx/Konnect/issues/328) | P1 | Make shared connectivity bus-aware. |
| [#331](https://github.com/mixelpixx/Konnect/issues/331) | P1 | Preserve `fp_text user` during library refresh. |

## Roadmap and contribution follow-through

The roadmap direction remains useful but its status is stale: #273 and #120
have shipped, the v0.8 skill-layer gate has passed, and it tells contributors
to claim Freerouting on closed #253. It should be updated to the post-v0.9
rendering, placement and gate work without changing the still-valid
Freerouting direction.

The unchanged contribution rules still require issue-first design agreement,
focused PRs, compatibility handling for public contracts, tests, doc tests,
warnings-denied Clippy, formatting, real-KiCad fixtures for board/footprint
parsing, structured argument validation and synchronized tool counts.

Recommended order:

1. Review and land #333, then release and verify the #326 round trip.
2. Repair #334 and use it to implement #240 with #241 evidence.
3. Rebase and narrow #270 for #252.
4. Finish the remaining #182 reads, then bound #189.
5. Fix #331 and #328; keep #315 as its own connected-move series.
6. Agree on the Freerouting DSN/SES architecture and issue, then implement it
   as a short, testable PR series.
7. Resolve #103/#242 and compact-client discovery (#233/#325).
8. Rebase, narrow or close stale conflicting PRs before adding overlapping work.

Refresh this backlog whenever a release changes the issue/PR inventory or the
post-tag rendering and placement work becomes part of a published contract.
