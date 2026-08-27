# Konnect v0.9.0 synchronization research

Primary-source inventory captured 26-Aug-2026 for the Konnect fork, the
standalone `konnect-codex` companion, and the improvement backlog in
[Discussion #165](https://github.com/mixelpixx/Konnect/discussions/165).

## Executive conclusion

Konnect v0.9.0 is a real release boundary, but upstream `main` has already moved
well past it. Treat these as two separate synchronization targets:

1. **Version-match `konnect-codex` to the v0.9.0 tag.** The released server is
   [tag commit `8648fe25`](https://github.com/mixelpixx/Konnect/commit/8648fe2573377eac78525907cbdd16216986f08e).
2. **Synchronize the `neusse/Konnect` fork's `main` to upstream `main`.** At this
   snapshot upstream is [`2b5a33f`](https://github.com/mixelpixx/Konnect/commit/2b5a33f62a087d54b670ac41a93f4d1827c1b4e9),
   17 commits beyond the tag, with substantial unreleased rendering, visual
   baseline, geometry, design-hash and placement-scoring work.

Do not describe post-tag `main` capabilities as v0.9.0 capabilities. The
companion release should require the tagged release contract; optional support
for newer `main` tools can be feature-detected, but should not become a v0.9.0
requirement.

## Release and branch facts

- [v0.9.0 release](https://github.com/mixelpixx/Konnect/releases/tag/v0.9.0),
  published 25-Aug-2026 at 20:51 UTC, is titled **“the truth-in-responses
  release.”**
- The complete [v0.8.0...v0.9.0 comparison](https://github.com/mixelpixx/Konnect/compare/v0.8.0...v0.9.0)
  contains 36 commits and 37 changed files.
- The tag exposes **`toolset_count: 19`, 206 registered tools and 212 total tools**.
- Current upstream `main` is [17 commits past v0.9.0](https://github.com/mixelpixx/Konnect/compare/v0.9.0...main),
  across 46 changed files, and exposes **20 toolsets, 210 registered tools and
  216 total tools**.
- [CONTRIBUTING.md](https://github.com/mixelpixx/Konnect/blob/main/CONTRIBUTING.md)
  did not change between v0.8.0, v0.9.0 and the current `main` snapshot.

## What v0.9.0 shipped

The release's nine merged pull requests establish these changes:

- [PR #232](https://github.com/mixelpixx/Konnect/pull/232) adds the dry-run,
  revision-gated, atomic `update_footprints_from_library` tool and closes
  [#231](https://github.com/mixelpixx/Konnect/issues/231).
- [PR #264](https://github.com/mixelpixx/Konnect/pull/264) adds atomic
  `set_component_placements`, with a single snapshot/commit/undo operation and
  post-commit readback.
- [PR #330](https://github.com/mixelpixx/Konnect/pull/330) reconciles junction
  dots after schematic component movement and closes
  [#120](https://github.com/mixelpixx/Konnect/issues/120). It does not implement
  wire-carrying `move_connected`, which remains [#315](https://github.com/mixelpixx/Konnect/issues/315).
- [PR #273](https://github.com/mixelpixx/Konnect/pull/273) makes reference-based
  schematic mutations operate on every placed unit of a multi-unit component.
  [#182](https://github.com/mixelpixx/Konnect/issues/182) remains open for other
  unit-1-only readers and analyses.
- [PR #265](https://github.com/mixelpixx/Konnect/pull/265) makes live pad
  readback fail instead of fabricating or dropping values and names all
  representable layers.
- [PR #275](https://github.com/mixelpixx/Konnect/pull/275) changes schematic
  layout and overlap checks from component origins to transformed symbol
  geometry.
- The release also fixes `add_bus_entry` endpoint reporting from actual sheet
  geometry, closing [#329](https://github.com/mixelpixx/Konnect/issues/329), and
  merges dependency PRs [#243](https://github.com/mixelpixx/Konnect/pull/243),
  [#320](https://github.com/mixelpixx/Konnect/pull/320), and
  [#321](https://github.com/mixelpixx/Konnect/pull/321).

### New release limitations that must remain visible

- [#331](https://github.com/mixelpixx/Konnect/issues/331):
  `update_footprints_from_library` correctly refuses most official KiCad
  footprints because `fp_text user` is not yet representable. The issue measured
  393 failures in a sample of 400 official KiCad-10 footprints. This is a safe
  refusal, but it makes the headline tool unavailable for the dominant library
  case.
- [#315](https://github.com/mixelpixx/Konnect/issues/315): `move_connected`
  still refuses; the v0.9.0 junction work is only its prerequisite.
- [#328](https://github.com/mixelpixx/Konnect/issues/328): shared schematic
  connectivity remains bus-blind.
- [#221](https://github.com/mixelpixx/Konnect/issues/221): the live-test CI claim
  and rotation-readback flake remain unresolved.

## Post-v0.9.0 upstream `main`

These are important for the fork, but are not part of the tagged release:

- Gate/verdict contracts, design hashes and sourcing-policy defaults were added
  in [`6bcf743`](https://github.com/mixelpixx/Konnect/commit/6bcf7438b73b7592d0590be9db9fed0973a41f84)
  and [`abde7d6`](https://github.com/mixelpixx/Konnect/commit/abde7d646046a4d2b46cd0b8ad4f3d6e69b81463).
- PCB tracks, vias, zones, outline geometry, courtyards and connectivity gained
  structural parsing in [`df42827`](https://github.com/mixelpixx/Konnect/commit/df42827b93846068c290c4595cb09c4d58b56d19)
  and [`8ede246`](https://github.com/mixelpixx/Konnect/commit/8ede246d6f00fbd145d7f69ab6f5946b93caba71).
- `render_schematic_png` landed in
  [`817a64a`](https://github.com/mixelpixx/Konnect/commit/817a64a5b99d1c5c50a54c3104f08daa09a9824d),
  and visual baseline capture/comparison in
  [`412d44c`](https://github.com/mixelpixx/Konnect/commit/412d44ca30d3acbbe50bfbce31f271d6717fa6f9).
- `score_placement` became the first tool in a new `placement` toolset in
  [`668af70`](https://github.com/mixelpixx/Konnect/commit/668af70808a754acf4c24c60bfd5dae6d1209a53)
  and [`2b5a33f`](https://github.com/mixelpixx/Konnect/commit/2b5a33f62a087d54b670ac41a93f4d1827c1b4e9).
- `konnect-render`, `konnect-vcs`, third-party attribution, dependency-license
  CI and real KiCad variant/placement fixtures are now in the tree.

These features align strongly with the companion's existing schematic visual
gate and PCB placement gate. Once they are released, the companion should use
Konnect's `render_schematic_png`, baseline comparison and `score_placement` as
native evidence sources instead of duplicating those judgments. For a v0.9.0
companion, they should be documented only as optional post-tag capabilities.

## Upstream guidance delta and companion impact

Konnect still ships **six Claude skills and two Claude agents**, represented by
17 tracked guidance files. No upstream agent changed in v0.9.0. Exactly two
skill files changed:

1. [`kicad-library/SKILL.md`](https://github.com/mixelpixx/Konnect/blob/v0.9.0/crates/konnect/assets/skills/kicad-library/SKILL.md)
   now loads `pcb_components` and documents dry-run/apply behavior for
   `update_footprints_from_library`.
2. [`kicad-pcb/SKILL.md`](https://github.com/mixelpixx/Konnect/blob/v0.9.0/crates/konnect/assets/skills/kicad-pcb/SKILL.md)
   adds footprint-library refresh between schematic transfer and placement.

Required `konnect-codex` changes:

- Bump `Cargo.toml`, `compatibility.json`, badges, install examples, release
  notes and the exact upstream commit to v0.9.0 / `8648fe25`.
- Recompute the upstream 17-file baseline and guidance fingerprint after
  reviewing the two changed skills. Do not merely replace the hashes.
- Add the safe library-refresh workflow to the Codex library/PCB skills, but
  explicitly surface #331 and refuse to claim that official-library refresh
  works when `fp_text user` is present.
- Teach the PCB builder to prefer `set_component_placements` for an already
  approved batch placement: one atomic call, one undo entry, and readback of
  what KiCad actually stored.
- Remove the temporary #329 reversed-endpoint warning. Keep the #328 bus-blind
  validation warning.
- Replace the old #120 warning with the narrower truth: ordinary component
  moves reconcile affected junctions in v0.9.0, while `move_connected` remains
  unavailable under #315.
- Keep the #326 Default-netclass safety gate until its fix is merged and
  released. [PR #333](https://github.com/mixelpixx/Konnect/pull/333) is not in
  v0.9.0.
- Keep the companion's Freerouting bridge unchanged for this release. Konnect
  still has no public `autoroute` tool. The companion bridge is a KiCad-10
  evidence source and non-overwriting workflow, not a Rust/IPC implementation
  that can be copied upstream.
- After publishing, run the companion's sync/doctor checks and restart MCP
  sessions so the installed plugin does not keep v0.8.0 guidance in memory.

The local `konnect-codex` worktree contains a pre-existing modification to
`test-projects/hub75-controller-final/hub75_controller_final.kicad_pro`; it must
not be staged or altered during the release work.

## Freerouting direction

The current [ROADMAP Freerouting section](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md#3-autorouting-a-real-freerouting-bridge)
still adopts the design from #253: drive a standalone JAR, distinguish engine
discovery from bridge readiness, validate board identity, and import atomically.
The latest maintainer response in [Discussion #165](https://github.com/mixelpixx/Konnect/discussions/165#discussioncomment-18149346)
explicitly says Freerouting is his preferred item for us to take.

The architectural blocker remains real: running the Freerouting JAR is a normal
headless Java subprocess and needs no computer-use automation, but durable DSN
export and SES import are not exposed by the currently supported KiCad IPC
surface. The companion uses KiCad's legacy Python/SWIG path, while
[#257](https://github.com/mixelpixx/Konnect/issues/257) tracks its removal in
KiCad 11. The next upstream action should therefore be architecture agreement,
not a promise to copy the companion implementation.

Because #253 is closed while the roadmap says to claim implementation there,
ask the maintainer whether to reopen #253 or create a focused implementation
issue. Then use a short PR series under the contribution rules: contract and
capability reporting; DSN producer; SES parser/dry-run plan; atomic IPC apply;
public autoroute workflow and end-to-end evidence.

## Current open pull requests

Status is volatile; refresh it immediately before publishing the backlog.

| PR | Snapshot assessment |
| --- | --- |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) | Conflicting and stale. A POSIX process `exec` is not a complete #103/#242 or Windows lifecycle solution. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) | Conflicting. Reduce to nested-validation coverage not already merged for #234. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) | Conflicting but still the main implementation path for #252 artifact verification. |
| [#322](https://github.com/mixelpixx/Konnect/pull/322) | Mergeable and checks green; replaces escaped/multiline library-field text scans with structural reads. |
| [#332](https://github.com/mixelpixx/Konnect/pull/332) | Mergeable and checks green; tests the sheet-pin branch of v0.9 junction reconciliation. |
| [#333](https://github.com/mixelpixx/Konnect/pull/333) | Mergeable and checks green; active fix for P0 #326. Review whether its second, caller-visible netclass-response refactor belongs in the same PR. |
| [#334](https://github.com/mixelpixx/Konnect/pull/334) | Shared IPC classification gate and board mock; useful #240/#241 groundwork, but platform checks were failed/cancelled at this snapshot. |
| [#335](https://github.com/mixelpixx/Konnect/pull/335) | Stacked on #334 and conflicting with current main. Rebase and reconcile its stated append behavior with the already-closed #314 outline replacement before considering it. |

## Complete open-issue disposition

There are **30 open issues** at this snapshot.

| Issue | Priority | Updated disposition |
| --- | --- | --- |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) | P1 | Finish structural replacement of indentation/line-ending-sensitive scans. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) | P1 | Server-owned multi-instance lifecycle and orphan cleanup remain open. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) | P2 | Add a true layer-aware 2-D board plot; current top render is 3-D. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) | P1 | Bound and complete DRC output, including output-path handling. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) | P1 | Sign/notarize both macOS slices and final artifacts. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) | P2 | Homebrew after signed artifacts stabilize. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) | P3 | Preserve lock-name compatibility before the `sha2` upgrade. |
| [#182](https://github.com/mixelpixx/Konnect/issues/182) | P0 | v0.9 fixes multi-unit mutation; finish remaining unit-1-only batch/export/analysis/review reads. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) | P0 | Bound root/library-table discovery and refuse ambiguity. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) | P2 | Reduce whole-sheet reserialization diff churn. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) | P1 | Make live-CI claims real and fix rotation-readback flakiness. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) | P2 | Select footprint graphics by stable identity, not only by layer. |
| [#226](https://github.com/mixelpixx/Konnect/issues/226) | P3 | Restore placed Datasheet/Description fidelity based on measured impact. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) | P1 | Support clients that never re-fetch changed tool lists. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) | P0 | Refuse stale file fallback after an observed-live board loses IPC. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) | P1 support | Provide the reusable document-answering IPC mock needed by #240. |
| [#242](https://github.com/mixelpixx/Konnect/issues/242) | P1 | Starting the MCP server must not silently reinstall guidance. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) | P0 | Verify every reported artifact; #270 needs reconciliation. |
| [#254](https://github.com/mixelpixx/Konnect/issues/254) | P1 | Discover supported per-user Windows KiCad installs. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) | P1 | Open and prove the exact requested PCB document. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) | P1/deadline | Plan KiCad 11 lifecycle and eliminate legacy SWIG dependencies. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) | P1 | Add explicit custom-field upsert to batch schematic edits. |
| [#291](https://github.com/mixelpixx/Konnect/issues/291) | P1 | Honor or reject the requested schematic SVG filename; the post-tag PNG renderer does not close this. |
| [#296](https://github.com/mixelpixx/Konnect/issues/296) | P2 | Continue advanced symbol/footprint generation as focused tool plus guidance PRs. |
| [#305](https://github.com/mixelpixx/Konnect/issues/305) | P2 | Add a supported placed-footprint 3-D model edit path. |
| [#315](https://github.com/mixelpixx/Konnect/issues/315) | P1 | Implement actual connected wire movement; v0.9 only completed its junction prerequisite. |
| [#325](https://github.com/mixelpixx/Konnect/issues/325) | P1 | Add a compact call/help surface and/or MCP resource directory for capped clients. |
| [#326](https://github.com/mixelpixx/Konnect/issues/326) | P0, active | Preserve the complete Default netclass; #333 is the green active fix. |
| [#328](https://github.com/mixelpixx/Konnect/issues/328) | P1 | Make the shared connectivity index bus- and bus-entry-aware. |
| [#331](https://github.com/mixelpixx/Konnect/issues/331) | P1 | Support standard `fp_text user` without losing artwork, proven by apply/save/noop convergence. |

## Exact improvement-backlog edits

Update [Discussion #165](https://github.com/mixelpixx/Konnect/discussions/165)
and `docs/IMPROVEMENT_BACKLOG.md` as follows:

- Change the title/date and release snapshot to v0.9.0 at `8648fe25`.
- Give post-release `main` its own snapshot at `2b5a33f`; do not fold those
  tools into the released feature list.
- Change inventory from 32 issues / 13 PRs to **30 issues / eight PRs**.
- Change release counts from 19 / 204 / 210 to **19 / 206 / 212**.
- Mark #120, #231 and #329 completed.
- Mark PRs #232, #243, #264, #265, #273, #275, #320, #321 and #330 merged.
- Replace the old broad #182 text with its remaining read/analysis scope.
- Replace #231's backlog entry with #331's narrower production limitation.
- Move #326 to “active fix in #333,” while retaining it at P0 until a release
  actually contains the fix.
- Preserve #315 separately from completed #120.
- Add post-tag schematic PNG/baseline and placement scoring as evidence that
  the next native workflow layer is already being built.
- Keep Freerouting prominent and record the maintainer's explicit preference,
  but state the DSN/SES IPC decision as the current design blocker.
- Replace the open-PR table with the eight-current-PR table above.

## Roadmap drift to call out

The current [ROADMAP.md](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md)
predates v0.8.0 and is now stale in four important ways:

- it says #273 lands next, but #273 shipped in v0.9.0;
- it treats #120 as open, although #120 closed and #315 is now the remaining
  connected-move work;
- it says the skill-layer work is gated on v0.8.0, a gate that has passed;
- it tells contributors to claim Freerouting on closed #253.

The post-v0.9 rendering, visual-baseline, placement-scoring and gate/design-hash
work also needs to be reflected. This is documentation drift, not a change in
the still-valid Freerouting direction.

## Contribution requirements for follow-on work

The unchanged [contributor rules](https://github.com/mixelpixx/Konnect/blob/main/CONTRIBUTING.md)
still require:

- issue-first design agreement for nontrivial changes;
- focused PRs, split by platform/protocol/feature/documentation outcome;
- compatibility handling for every public tool/schema/config change;
- all four Rust gates (`test` libraries/tests, doc tests, clippy with warnings
  denied, and formatting);
- real-KiCad fixtures for board/footprint parsing;
- structured required-argument and layer validation; and
- synchronized tool counts whenever the public tool surface changes.

These requirements strongly favor a staged Freerouting series rather than one
large bridge PR.
