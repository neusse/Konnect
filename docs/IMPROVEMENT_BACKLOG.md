# Konnect improvement backlog — 27-Aug-2026 (v0.10.0)

> **Disclosure.** This is a Codex-assisted evaluation based on the v0.10.0
> release and source, the current roadmap and contribution rules, every open
> issue, every open pull request, relevant merged/closed work, maintainer
> feedback in Discussions, and our end-to-end KiCad use through the
> version-matched `konnect-codex` companion plugin. Priorities are
> recommendations, not maintainer assignments. We will continue to claim work
> on its issue, agree on the design, and submit focused, tested PRs.

## Snapshot

- Released contract: [v0.10.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.10.0),
  tag commit [`866933e`](https://github.com/mixelpixx/Konnect/commit/866933e8aca1c115479963463cc7e34370b5822b).
- Released surface: **20 toolsets, 214 registered tools, 220 total tools**.
- Current upstream `main`: [`e2a204b`](https://github.com/mixelpixx/Konnect/commit/e2a204bb4b1b676d44c18d98fb72fa7daefd5e30),
  one packaging-stamp commit beyond the tag with the same public tool surface.
- Live inventory: **34 open issues and 19 open pull requests**.
- Local environment: exact v0.10.0 Konnect plus `konnect-codex` v0.10.0;
  compatibility audit and doctor both pass with 8 reviewed skills, 5 agents,
  and 22 active companion enhancements.

## Executive assessment

v0.10.0 is the first release in which an agent can natively see and score part
of its own work. Schematic PNG rendering, visual baselines, placement scoring,
decoupling placement, BGA fanout planning, connectivity clustering, and
force-directed refinement close important feedback loops identified in
[Discussion #295](https://github.com/mixelpixx/Konnect/discussions/295).

The release also exposes a new P0 defect:
[#350](https://github.com/mixelpixx/Konnect/issues/350) shows that
`auto_place_from_schematic` moves KiCad-locked footprints and offers no safe
subset/exemption control. Dry-run-by-default limits immediate damage, but apply
cannot yet preserve enclosure- and connector-constrained placement.

The existing P0 queue remains real. #326 has a green fix; #240 has test/mock
groundwork but not the stale-live-board policy; #252 has a conflicting old PR;
#189 is awaiting a maintainer choice; and #182 has a green partial draft while
`design_review` remains unit-blind. The Freerouting work requested by the
maintainer is now an active, tested four-PR stack rather than an unowned design.

## What v0.10.0 shipped

- `render_schematic_png`, `set_visual_baseline`, and
  `compare_visual_baseline` provide deterministic visual feedback.
- The new placement toolset adds `score_placement`,
  `place_decoupling_caps`, `plan_bga_fanout`,
  `auto_place_from_schematic`, and `refine_placement_force_directed`.
- PCB parsing now covers tracks, vias, zones, exact outline bounds,
  transformed courtyards, and net-to-geometry connectivity.
- Gate/verdict contracts distinguish `BLOCKED` from `PASS`; canonical design
  hashes are line-ending independent.
- Konnect's native PCB and schematic skills gained score-first placement and
  visual-feedback guidance. The v0.10 `konnect-codex` release reviewed and
  integrated those changes into its stronger PCB/schematic workflow gates.

## P0 — correctness and non-destructive behavior

### 1. Never move constrained placement — #350

[#350](https://github.com/mixelpixx/Konnect/issues/350) should be the first
v0.10 hotfix. `auto_place_from_schematic` must honor KiCad's `(locked)` state,
report skipped footprints, and support explicit inclusion/exemption. The
measured real-board evidence matters: only 12 of 42 footprints with plated or
unplated through holes were locked, so honoring locks alone still moves 30
mechanically constrained parts. Count `thru_hole` and `np_thru_hole`; do not
guess from reference prefixes.

### 2. Preserve the complete Default netclass — #326 / PR #333

[#326](https://github.com/mixelpixx/Konnect/issues/326) can omit `wire_width`
and make Eeschema suppress junction dots project-wide.
[PR #333](https://github.com/mixelpixx/Konnect/pull/333) is mergeable and green.
Land it, then prove a saved/reopened T-junction project remains connected and
ERC-clean.

### 3. Refuse stale-file mutation after live IPC loss — #240 / #241 / PR #334

[#240](https://github.com/mixelpixx/Konnect/issues/240) remains the central
wrong-state hazard. [PR #334](https://github.com/mixelpixx/Konnect/pull/334)
now provides a mergeable shared IPC classification gate and document-answering
mock, but it is groundwork rather than the policy fix. Bind mutators to observed
document identity and fail closed if a formerly live editor disappears.

### 4. Verify every reported artifact — #252 / PR #270

[#252](https://github.com/mixelpixx/Konnect/issues/252) still requires path,
existence, nonzero-size, signature, revision/board identity, and per-artifact
evidence. [PR #270](https://github.com/mixelpixx/Konnect/pull/270) is now
conflicting and contains obsolete overlap. Prefer a clean, current-main PR
rather than preserving its historical stack mechanically.

### 5. Finish unit-aware reads and reviews — #182 / PRs #349 and #336

[PR #349](https://github.com/mixelpixx/Konnect/pull/349) is a green draft that
fixes the remaining `sch_analysis`/`sch_export` paths and proves `sch_batch`
handlers against the real ECC83 fixture. It deliberately does not close
[#182](https://github.com/mixelpixx/Konnect/issues/182):
[PR #336](https://github.com/mixelpixx/Konnect/pull/336) still needs the same
per-unit pin resolution in `design_review` before the umbrella issue is done.

### 6. Bound project ownership — #189

[#189](https://github.com/mixelpixx/Konnect/issues/189) can resolve a loose
schematic through an unrelated ancestor project. The sound discriminator is
sheet-tree membership, not path depth, `$HOME`, or a Git boundary. Reuse the
depth-bounded, cycle-safe ownership traversal; accept exactly one verified
owner and return a structured conflict naming candidate roots when ownership
cannot be established. The maintainer still needs to confirm this policy.

## P1 — high-value workflow reliability

### Freerouting: active implementation, not backlog speculation

The requested bridge is now split into focused, current-v0.10 PRs:

1. [#338](https://github.com/mixelpixx/Konnect/pull/338) — revision-bound DSN
   export plus reverse manifest and external Freerouting corpus.
2. [#339](https://github.com/mixelpixx/Konnect/pull/339) — strict SES planning
   and atomic IPC apply, including validated `qarc` conversion.
3. [#340](https://github.com/mixelpixx/Konnect/pull/340) — local Freerouting
   2.3.0 native MCP orchestration, schema validation, diagnostics, timeouts,
   and child cleanup.
4. [#342](https://github.com/mixelpixx/Konnect/pull/342) — optional,
   authenticated KiCad 10 native DSN-export bridge with Rust fallback.

All four were rebased after v0.10 landed. Their PRs explicitly record the
release-10 blind-side changes to catalogue totals and public contracts, and the
stack has passed real Freerouting 2.3.0 routing. Merge in dependency order.

### Ready or nearly ready

- [#331](https://github.com/mixelpixx/Konnect/issues/331) /
  [PR #348](https://github.com/mixelpixx/Konnect/pull/348): preserve official
  footprint `fp_text user` through refresh. Current, green, mergeable.
- [#254](https://github.com/mixelpixx/Konnect/issues/254) /
  [PR #344](https://github.com/mixelpixx/Konnect/pull/344): discover per-user
  Windows KiCad installs and report unresolved library roots. Green.
- [#242](https://github.com/mixelpixx/Konnect/issues/242) /
  [PR #343](https://github.com/mixelpixx/Konnect/pull/343): make MCP startup
  non-mutating and require explicit guidance installation. Green.
- [#325](https://github.com/mixelpixx/Konnect/issues/325) /
  [PR #347](https://github.com/mixelpixx/Konnect/pull/347): document client
  tool-cap limits. Green draft; documentation, not a protocol fix.
- [#345](https://github.com/mixelpixx/Konnect/issues/345) /
  [PR #346](https://github.com/mixelpixx/Konnect/pull/346): expose router
  predefined track/via palettes without conflating them with constraints or
  netclasses.

### Still unclaimed or incomplete

- [#328](https://github.com/mixelpixx/Konnect/issues/328): make the shared
  connectivity model bus-aware; KiCad ERC remains authoritative meanwhile.
- [#315](https://github.com/mixelpixx/Konnect/issues/315): implement real
  connected-wire movement; the current honest refusal is safer than the old
  false success.
- [#103](https://github.com/mixelpixx/Konnect/issues/103): core server-owned,
  multi-instance lifecycle remains open. Companion session cleanup mitigates
  Codex use but does not fix Konnect itself.
- [#256](https://github.com/mixelpixx/Konnect/issues/256): open and prove the
  exact requested PCB document.
- [#257](https://github.com/mixelpixx/Konnect/issues/257): KiCad 11 SWIG-removal
  and deprecated-IPC migration remains a release deadline.
- [#291](https://github.com/mixelpixx/Konnect/issues/291): honor or reject the
  requested SVG filename; v0.10 PNG rendering does not close it.
- [#305](https://github.com/mixelpixx/Konnect/issues/305): placed-footprint 3-D
  model editing remains useful after the common library-refresh path in #348.

## Open pull-request assessment

| PR | Current state | Assessment |
| --- | --- | --- |
| [#349](https://github.com/mixelpixx/Konnect/pull/349) | Draft, green, mergeable | Correct partial #182 scope; wait for review and coordinate #336. |
| [#348](https://github.com/mixelpixx/Konnect/pull/348) | Green, mergeable | Focused #331 fix; refreshed for v0.10. |
| [#347](https://github.com/mixelpixx/Konnect/pull/347) | Draft, green, mergeable | Useful Copilot guidance; does not solve client filtering. |
| [#346](https://github.com/mixelpixx/Konnect/pull/346) | Green, mergeable | Clear separation of router palette from constraints/netclasses. |
| [#344](https://github.com/mixelpixx/Konnect/pull/344) | Green, mergeable | Windows user-install discovery plus actionable failure evidence. |
| [#343](https://github.com/mixelpixx/Konnect/pull/343) | Green, mergeable | Removes startup side effects; explicit init remains. |
| [#342](https://github.com/mixelpixx/Konnect/pull/342) | Mergeable; CI rerun | Fourth Freerouting layer; merge after #338-#340. |
| [#340](https://github.com/mixelpixx/Konnect/pull/340) | Green, mergeable | Native MCP orchestration; real engine route and cleanup proven. |
| [#339](https://github.com/mixelpixx/Konnect/pull/339) | Green, mergeable | Strict atomic SES import including quarter arcs. |
| [#338](https://github.com/mixelpixx/Konnect/pull/338) | Green, mergeable | First Freerouting layer; merge first. |
| [#336](https://github.com/mixelpixx/Konnect/pull/336) | Green, mergeable | Net-graph design review fix; must become unit-aware for #182. |
| [#335](https://github.com/mixelpixx/Konnect/pull/335) | Conflicting | Rebase/narrow against current outline semantics. |
| [#334](https://github.com/mixelpixx/Konnect/pull/334) | Green, mergeable | Useful #240/#241 groundwork, not the policy completion. |
| [#333](https://github.com/mixelpixx/Konnect/pull/333) | Green, mergeable | Active P0 #326 fix. |
| [#332](https://github.com/mixelpixx/Konnect/pull/332) | Green, mergeable | Focused junction sheet-pin coverage. |
| [#322](https://github.com/mixelpixx/Konnect/pull/322) | Green, mergeable | Structural library/table field parsing. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) | Conflicting | Replace with a clean current-main artifact-verification PR. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) | Conflicting | Reassess remaining coverage after shipped validation work. |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) | Conflicting, stale | POSIX reload is not a complete Windows/multi-instance lifecycle design. |

## Complete open-issue disposition

| Issue | Priority | Disposition |
| --- | --- | --- |
| [#350](https://github.com/mixelpixx/Konnect/issues/350) | P0 | Preserve locked/mechanically constrained footprints in auto-place. |
| [#345](https://github.com/mixelpixx/Konnect/issues/345) | P1 active | Router palette implementation in #346. |
| [#341](https://github.com/mixelpixx/Konnect/issues/341) | P1 active | KiCad 10 native DSN bridge in #342. |
| [#337](https://github.com/mixelpixx/Konnect/issues/337) | P1 active | Freerouting stack #338/#339/#340; #342 optional fast path. |
| [#331](https://github.com/mixelpixx/Konnect/issues/331) | P1 active | Preserve library user text; #348 green. |
| [#328](https://github.com/mixelpixx/Konnect/issues/328) | P1 | Bus-aware connectivity. |
| [#326](https://github.com/mixelpixx/Konnect/issues/326) | P0 active | Complete Default netclass; #333 green. |
| [#325](https://github.com/mixelpixx/Konnect/issues/325) | P1 | Client tool-limit guidance #347; protocol capability remains. |
| [#315](https://github.com/mixelpixx/Konnect/issues/315) | P1 | Real connected-wire movement. |
| [#305](https://github.com/mixelpixx/Konnect/issues/305) | P2 | Placed-footprint 3-D model editing after #348. |
| [#296](https://github.com/mixelpixx/Konnect/issues/296) | P2 | Focused symbol/footprint controls plus workflow guidance. |
| [#291](https://github.com/mixelpixx/Konnect/issues/291) | P1 | Correct SVG output filename contract. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) | P1 | Batch custom-field upsert. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) | P1 deadline | KiCad 11 plugin/IPC migration. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) | P1 | Open and prove exact board identity. |
| [#254](https://github.com/mixelpixx/Konnect/issues/254) | P1 active | Per-user Windows discovery in #344. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) | P0 | Clean current-main artifact verification PR needed. |
| [#242](https://github.com/mixelpixx/Konnect/issues/242) | P1 active | Explicit-only guidance installation in #343. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) | P0 support | Shared document-answering mock in #334. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) | P0 | Refuse stale fallback after observed-live IPC loss. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) | P1 | Linux toolset loading/client reachability evidence. |
| [#226](https://github.com/mixelpixx/Konnect/issues/226) | P3 | Restore Datasheet/Description fidelity by measured impact. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) | P2 | Select footprint graphics by stable identity. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) | P1 | Make live-CI claims real and fix fixture/race. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) | P2 | Reduce whole-sheet serialization diff churn. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) | P0 decision | Membership-based ownership plus structured conflict. |
| [#182](https://github.com/mixelpixx/Konnect/issues/182) | P0 active | #349 partial; coordinate unit-aware design review in #336. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) | P3 | Preserve lock-name compatibility before sha2 bump. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) | P2 | Homebrew after signing/release artifacts stabilize. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) | P1 release | Sign/notarize both macOS slices and final artifact. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) | P1 | Bound and preserve complete DRC output. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) | P2 | True layer-aware 2-D plot. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) | P1 | Core multi-session ownership and orphan cleanup. |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) | P1 | Finish structural parsing conversions. |

## Recommended execution order

1. Hotfix #350, then land and live-verify #333/#326.
2. Merge Freerouting in stack order #338 → #339 → #340 → #342.
3. Land #348, #344, and #343; move #347 out of draft when its documentation
   scope is accepted.
4. Coordinate #349 with the unit-aware correction in #336, then close #182.
5. Land #334 and implement the actual #240 policy with #241 evidence.
6. Replace #270 with a clean current-main #252 implementation.
7. Confirm and implement the membership-based #189 policy.
8. Continue #328, #315, #103, and the KiCad 11 #257 transition as independent
   focused series.

The rewritten [ROADMAP.md](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md)
now treats this backlog and the benchmark discussions as planning input. Keep
that dependency order, but update roadmap status when these active PRs merge so
the next contributor does not rebuild already-finished work.
