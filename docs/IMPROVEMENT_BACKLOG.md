# Konnect improvement backlog — 25-Aug-2026 (v0.8.0)

> **Disclosure.** I posted this Codex-assisted evaluation after reviewing the
> Konnect v0.8.0 release and source, the current roadmap and contributor rules,
> every open issue, every open pull request, relevant closed/merged work,
> maintainer responses, project discussions, and our actual end-to-end KiCad
> use with the version-matched `konnect-codex` plugin. The priorities below are
> recommendations, not maintainer assignments. Before implementing an item, I
> will claim it on the issue, agree on the design, and follow the roadmap and
> contribution process with one focused PR.

## Snapshot

- Release reviewed: [v0.8.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.8.0),
  tag commit [`dee8a27`](https://github.com/mixelpixx/Konnect/commit/dee8a27ce606f644cef0220deac98e88640d9b16).
- Current upstream `main`: [`c68c745`](https://github.com/mixelpixx/Konnect/commit/c68c745c2a26808726a477b2ef8e56e05833bdc0),
  one metadata-only PCM packaging commit ahead of the tag.
- Release delta: 98 commits and 61 changed files since v0.7.0.
- Live inventory at this snapshot: **32 open issues and 13 open pull requests**.
- Tool surface: 19 toolsets, 204 registered tools, 210 total.
- Companion reviewed and installed: `konnect-codex` v0.8.0 companion revision 1.

## Executive assessment

v0.8.0 is a major reliability release. It closes 13 items from the 21-August
backlog, repairs legacy footprint corruption, fixes repeated board-outline
corruption, replaces `move_connected` false success with an honest refusal,
adds catalogue-wide schema parameter checks, and moves several PCB reads and
zone creation onto live IPC.

The top risk has changed. [#326](https://github.com/mixelpixx/Konnect/issues/326)
now belongs at P0 because `create_netclass` can omit `wire_width` from the
Default netclass, causing Eeschema to suppress or strip junction dots and
potentially change project-wide connectivity. The v0.8.0 shared connectivity
index also remains bus-blind (#328), and `add_bus_entry` reports its two
endpoints backwards (#329). These are small-looking defects with outsized
agent-workflow consequences.

## Released progress since v0.7.0

- [#294](https://github.com/mixelpixx/Konnect/pull/294) adds a dry-run-first,
  revision-gated `repair_corrupted_footprints` tool, proven against a real
  68-footprint board with 848 phantom pads.
- [#314](https://github.com/mixelpixx/Konnect/issues/314) fixes
  `set_board_size` appending overlapping Edge.Cuts on every call.
- [#315](https://github.com/mixelpixx/Konnect/issues/315) stops
  `move_connected` from claiming it preserved wires when it did not. The real
  connected-move capability remains open and depends on #120.
- [#285](https://github.com/mixelpixx/Konnect/pull/285) lands the #251
  parameter-honesty series and a catalogue-wide CI guard.
- [#307–#313](https://github.com/mixelpixx/Konnect/pull/307) and
  [#317](https://github.com/mixelpixx/Konnect/pull/317) fix idempotent edits,
  sheet movement, duplicated UUIDs, text justification, project library-table
  targeting, generated-pin positions, SVG return, and invalid sheet-pin syntax.
- [#323](https://github.com/mixelpixx/Konnect/pull/323) gives schematic
  connectivity tools one shared index; #262 resolves power symbols and #267
  respects intentional no-connects.
- [#316](https://github.com/mixelpixx/Konnect/pull/316) creates/refills zones
  through live IPC when possible and reports explicit live/file provenance.
- [#207](https://github.com/mixelpixx/Konnect/pull/207) reads board state and
  pads from the live board; #324 adds custom User paper dimensions.
- [#327](https://github.com/mixelpixx/Konnect/pull/327) uses the local JLCPCB
  catalogue Datasheet column before network lookup.
- [#306](https://github.com/mixelpixx/Konnect/pull/306) ships the approved
  developer architecture, tool, integration, testing, and release guides.

## P0 — correctness and non-destructive behavior

### 1. Preserve the complete Default netclass — #326

[`create_netclass` omits `wire_width`](https://github.com/mixelpixx/Konnect/issues/326),
and an incomplete Default netclass can disable or strip schematic junctions.

Recommended implementation:

- serialize every KiCad Default netclass field, including `wire_width`;
- use KiCad defaults when optional caller values are absent;
- round-trip a real project through KiCad and prove the full field set survives;
- verify T-junction connectivity and ERC before/after the mutation;
- add a regression test that fails if any required Default field disappears.

Until fixed, workflows should not create or overwrite Default without explicit
round-trip evidence.

### 2. Make schematic moves connectivity-safe — #120 and #315

[#120](https://github.com/mixelpixx/Konnect/issues/120) is the underlying
junction/connectivity problem; [#315](https://github.com/mixelpixx/Konnect/issues/315)
tracks the missing wire-carrying move. v0.8.0 correctly refuses instead of
lying. [PR #330](https://github.com/mixelpixx/Konnect/pull/330) is a useful,
green junction-on-move prerequisite, not a complete `move_connected` solution.

Land this as staged, testable work: reconcile affected junctions first, then
implement explicit wire stretching/shrinking, rotation and delete behavior,
with KiCad ERC and serialized connectivity fixtures at every stage.

### 3. Refuse stale-file mutation after live IPC loss — #240/#241

[#240](https://github.com/mixelpixx/Konnect/issues/240) remains the central
wrong-state hazard: after a tool has observed an open document, IPC loss must
not silently fall back to editing a stale file. [#241](https://github.com/mixelpixx/Konnect/issues/241)
should supply the reusable document-answering IPC test harness.

Every mutator should bind to the requested document identity, report its
source, and fail closed if a formerly live document becomes unavailable.

### 4. Finish unit-aware mutation — #182

The shared connectivity index improves reads, but mutation is still incomplete.
Rebase [PR #273](https://github.com/mixelpixx/Konnect/pull/273) over #323 and
prove multi-unit placement, movement, rotation, deletion, annotation, pin lookup,
and connectivity without duplicate references or cross-unit corruption.

### 5. Bound project-root and library discovery — #189

[#189](https://github.com/mixelpixx/Konnect/issues/189) can still select an
unrelated ancestor project or library table. Search must stop at an explicit
project boundary, expose candidates, and refuse ambiguity rather than choosing
the first match.

### 6. Verify every reported artifact — #252

[#252](https://github.com/mixelpixx/Konnect/issues/252) remains open even after
the schema-honesty work. Every snapshot, export and manufacturing response must
verify the requested output path, existence, nonzero size, format signature,
board/revision identity, and per-artifact failure state.

## P1 — high-value workflow reliability

### Bus and response correctness — #328/#329

- [#328](https://github.com/mixelpixx/Konnect/issues/328): make the shared
  connectivity index understand buses, bus entries and bus-attached labels.
  Until then, KiCad ERC is authoritative for bus sheets; agent guidance must not
  “repair” correct geometry from a Konnect-only orphan result.
- [#329](https://github.com/mixelpixx/Konnect/issues/329): return `bus_side` and
  `wire_side` from the endpoints actually written. Add all-orientation tests and
  require response geometry to equal serialized geometry.

### Lifecycle and client reachability — #103/#233/#242/#325

- [#103](https://github.com/mixelpixx/Konnect/issues/103): own server children,
  track multiple instances, and remove orphaned processes safely.
- [#242](https://github.com/mixelpixx/Konnect/issues/242): MCP startup must not
  reinstall guidance after an explicit uninstall. Use an explicit-init model or
  a durable tombstone distinct from “never installed.”
- [#233](https://github.com/mixelpixx/Konnect/issues/233) and
  [#325](https://github.com/mixelpixx/Konnect/issues/325): support clients that
  cap tools or do not refetch after dynamic loading. The roadmap's compact
  surface plus tool-directory resource is the right direction. Codex remains
  functional through eager toolsets and does not need a proxy today.

### Board identity, platform and mutation completeness

- [#256](https://github.com/mixelpixx/Konnect/issues/256): opening a requested
  PCB must prove that exact document became active.
- [#257](https://github.com/mixelpixx/Konnect/issues/257): remove KiCad 11 SWIG
  assumptions and move necessary DSN/SES/editor operations toward supported IPC.
- [#231](https://github.com/mixelpixx/Konnect/issues/231): provide a live,
  verified Update Footprints from Library path; rebase #232 and repeat real-KiCad evidence.
- [#254](https://github.com/mixelpixx/Konnect/issues/254): discover supported
  per-user Windows KiCad installations without a hard-coded Program Files path.
- [#258](https://github.com/mixelpixx/Konnect/issues/258): support explicit
  custom-field upsert in batch schematic edits.
- [#291](https://github.com/mixelpixx/Konnect/issues/291): honor or reject the
  requested schematic SVG filename instead of silently changing it.
- [#119](https://github.com/mixelpixx/Konnect/issues/119): bound, categorize and
  preserve complete DRC reporting.
- [#221](https://github.com/mixelpixx/Konnect/issues/221): make live-CI claims
  match actual coverage and fix the rotation read-back race.

### Freerouting bridge

Konnect v0.8.0 intentionally has no `autoroute` tool. The roadmap now adopts the
standalone-JAR DSN/export-route-SES/import bridge we recommended: distinguish
engine detection from bridge availability, bind the exact board, import
atomically, and verify placement/inventory/unrouted/short/DRC results. The
version-matched `konnect-codex` plugin already supplies a non-overwriting bridge
and remains an evidence source, not a Rust implementation dependency.

## P2/P3 — bounded enhancements and maintenance

- [#84](https://github.com/mixelpixx/Konnect/issues/84) — finish structural
  replacement of indentation-sensitive schematic scans. **P1** because it
  underpins correctness, but stage it behind active P0 mutations.
- [#118](https://github.com/mixelpixx/Konnect/issues/118) — real layer-aware 2-D board plot.
- [#131](https://github.com/mixelpixx/Konnect/issues/131) — sign/notarize both macOS slices and final artifact. **P1** release work.
- [#154](https://github.com/mixelpixx/Konnect/issues/154) — Homebrew after stable signed artifacts.
- [#181](https://github.com/mixelpixx/Konnect/issues/181) — preserve lock-name compatibility before `sha2` bump.
- [#210](https://github.com/mixelpixx/Konnect/issues/210) — reduce whole-sheet serialization diff churn.
- [#225](https://github.com/mixelpixx/Konnect/issues/225) — select footprint graphics by identity, not only layer.
- [#226](https://github.com/mixelpixx/Konnect/issues/226) — resolve placed metadata fidelity from measured impact.
- [#241](https://github.com/mixelpixx/Konnect/issues/241) — reusable open-document refusal mock; P2 support for P0 #240.
- [#296](https://github.com/mixelpixx/Konnect/issues/296) — advanced symbol/footprint generation as agreed focused PRs.
- [#305](https://github.com/mixelpixx/Konnect/issues/305) — add or deliberately route placed-footprint 3-D model editing.

## Completed since the 21-August backlog

| Issue | Released resolution |
| --- | --- |
| [#219](https://github.com/mixelpixx/Konnect/issues/219) | User paper dimensions through #324. |
| [#234](https://github.com/mixelpixx/Konnect/issues/234) | Required nested fields and missing-coordinate refusal through #268/#318. |
| [#251](https://github.com/mixelpixx/Konnect/issues/251) | Parameter-honesty consolidation and CI guard through #285. |
| [#255](https://github.com/mixelpixx/Konnect/issues/255) | Local-catalog datasheet lookup through #327. |
| [#286](https://github.com/mixelpixx/Konnect/issues/286) | Text justification through #308. |
| [#287](https://github.com/mixelpixx/Konnect/issues/287) | Sheet captions and pins move with the sheet through #309. |
| [#288](https://github.com/mixelpixx/Konnect/issues/288) | Fresh nested UUIDs on duplication through #310. |
| [#289](https://github.com/mixelpixx/Konnect/issues/289) | Correct project library-table targeting through #311. |
| [#290](https://github.com/mixelpixx/Konnect/issues/290) | Actual SVG result returned through #313. |
| [#292](https://github.com/mixelpixx/Konnect/issues/292) | Idempotent edits through #307. |
| [#293](https://github.com/mixelpixx/Konnect/issues/293) | Resolved generated-pin geometry through #312. |
| [#303](https://github.com/mixelpixx/Konnect/issues/303) | Valid sheet-pin rotation through #317. |
| [#304](https://github.com/mixelpixx/Konnect/issues/304) | Pre-6.0 footprint upgrade hint through #319. |

## Open pull-request assessment

“Conflicting” means the branch needs reconciliation; it is not a quality
verdict. Green status is recorded at this snapshot.

| PR | State | Backlog assessment |
| --- | --- | --- |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) reload server | Conflicting, stale | Supersede or redesign for #103/#242 rather than reviving broad old behavior. |
| [#232](https://github.com/mixelpixx/Konnect/pull/232) live footprint update | Conflicting | Rebase and repeat real-KiCad preservation evidence. |
| [#243](https://github.com/mixelpixx/Konnect/pull/243) setup-python v7 | Mergeable, green | Small CI dependency update. |
| [#264](https://github.com/mixelpixx/Konnect/pull/264) placement batch | Conflicting | Still useful after design confirmation and rebase. |
| [#265](https://github.com/mixelpixx/Konnect/pull/265) pad-read hardening | Draft, conflicting | Rebase only its remaining delta over merged #207. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) nested validation | Conflicting | Reduce to malformed-input coverage not already landed in #318/#285. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) artifact verification | Conflicting | Rebase and narrow to unresolved #252 behavior. |
| [#273](https://github.com/mixelpixx/Konnect/pull/273) multi-unit mutation | Conflicting | Rebase over #323; remains the main #182 implementation path. |
| [#275](https://github.com/mixelpixx/Konnect/pull/275) symbol bounds | Conflicting | Rebase after unit-aware work. |
| [#320](https://github.com/mixelpixx/Konnect/pull/320) viewer UUID update | Mergeable, green | Bounded dependency update. |
| [#321](https://github.com/mixelpixx/Konnect/pull/321) workspace UUID update | Mergeable, green | Bounded dependency update. |
| [#322](https://github.com/mixelpixx/Konnect/pull/322) structural library fields | Mergeable, Windows failing | Useful read path, not ready until Windows is green. |
| [#330](https://github.com/mixelpixx/Konnect/pull/330) junction reconciliation | Mergeable, green | High-priority partial #120 prerequisite; remove stray artifacts and preserve its explicit partial scope. |

## Complete open-issue disposition

| Issue | Priority | Current disposition |
| --- | --- | --- |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) | P1 | Finish structural schematic parsing in staged conversions. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) | P1 | Server ownership and multi-instance lifecycle. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) | P2 | Layer-aware 2-D board plot. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) | P1 | Bounded, complete DRC output. |
| [#120](https://github.com/mixelpixx/Konnect/issues/120) | P0 | Junction-safe move/delete; #330 is a partial prerequisite. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) | P1 | macOS signing/notarization. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) | P2 | Homebrew after signed artifacts stabilize. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) | P3 | Preserve lock-name compatibility before dependency bump. |
| [#182](https://github.com/mixelpixx/Konnect/issues/182) | P0 | Rebase and finish multi-unit mutation. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) | P0 | Bound root/library discovery and refuse ambiguity. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) | P2 | Reduce serialization diff churn. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) | P1 | Fix live-CI claims and rotation race. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) | P2 | Select footprint graphics by identity. |
| [#226](https://github.com/mixelpixx/Konnect/issues/226) | P3 | Resolve placed metadata fidelity with evidence. |
| [#231](https://github.com/mixelpixx/Konnect/issues/231) | P1 | Live Update Footprints from Library. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) | P1 | Client tool-list refresh/cap compatibility. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) | P0 | Refuse stale fallback after observed-live IPC loss. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) | P2 | Shared document-answering IPC test harness. |
| [#242](https://github.com/mixelpixx/Konnect/issues/242) | P1 | Remove startup guidance mutation. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) | P0 | Verify every reported artifact. |
| [#254](https://github.com/mixelpixx/Konnect/issues/254) | P1 | Per-user Windows KiCad discovery. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) | P1 | Open and prove the requested PCB document. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) | P1 | KiCad 11 IPC/SWIG transition. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) | P1 | Explicit custom-field upsert. |
| [#291](https://github.com/mixelpixx/Konnect/issues/291) | P1 | Honor or reject requested SVG filename. |
| [#296](https://github.com/mixelpixx/Konnect/issues/296) | P2 | Focused advanced symbol/footprint generation. |
| [#305](https://github.com/mixelpixx/Konnect/issues/305) | P2 | Route placed-footprint 3-D model editing. |
| [#315](https://github.com/mixelpixx/Konnect/issues/315) | P1 | Implement real connected move after #120. |
| [#325](https://github.com/mixelpixx/Konnect/issues/325) | P1 | Compact surface/resource directory for capped clients. |
| [#326](https://github.com/mixelpixx/Konnect/issues/326) | P0 | Preserve Default netclass and schematic junctions. |
| [#328](https://github.com/mixelpixx/Konnect/issues/328) | P1 | Make connectivity bus-aware. |
| [#329](https://github.com/mixelpixx/Konnect/issues/329) | P1 | Correct bus-entry response endpoints. |

## Recommended execution order

1. Claim and fix #326 with a full KiCad Default-netclass round trip.
2. Review/land the bounded part of #330, then continue #120/#315 in focused PRs.
3. Implement #240 with reusable #241 IPC document fixtures.
4. Rebase #273 for #182, then address #189 and #252.
5. Fix #328/#329 before trusting agent-driven bus cleanup.
6. Implement the roadmap Freerouting bridge with exact-board and import evidence.
7. Address #103/#242 and compact client discovery (#233/#325).
8. Rebase, narrow or close stale PRs before adding more overlapping work.

## Release and benchmark follow-through

The version-matched `konnect-codex` v0.8.0 plugin has been reviewed against all
17 upstream guidance files. It carries the three upstream skill changes plus
temporary safety gates for #315/#326/#328/#329, preserves the companion
Freerouting bridge, and removes the nonexistent Konnect `autoroute` hook.

The remaining evidence step is a v0.8.0 end-to-end benchmark that includes:

- structured schematic SVG return and visual readability inspection;
- a Default-netclass/junction probe for #326;
- a bus sheet that exposes #328/#329 until fixed;
- exact-board live reads and live zone creation;
- local-catalog datasheet resolution;
- footprint-corruption repair dry-run/apply evidence;
- transfer inventory, placement image, Freerouting provenance, route-import
  inventory, direct ERC/DRC, 3-D review, and manufacturing artifacts.

This backlog should be refreshed after that benchmark or whenever a new minor
release changes the issue/PR inventory.
