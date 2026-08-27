# Konnect v0.8.0 synchronization research

Snapshot: **2026-08-25**, after the v0.8.0 release. This report uses only
first-party GitHub material: the tagged release and source, current repository
state, issue and pull-request records, CI results, the project roadmap, API
migrations, and maintainer comments in the project discussions.

## Executive result

Konnect v0.8.0 is a major reliability release rather than a routine version
bump. It closes 13 items that were open in the August 21 improvement backlog,
repairs two additional silent-corruption/false-success defects discovered after
that snapshot, merges the developer documentation set, and makes the schema
parameter contract testable across the catalogue. The old backlog should not be
edited incrementally; its priorities and inventory need a full v0.8.0 rewrite.

The tagged release is
[`dee8a27`](https://github.com/mixelpixx/Konnect/commit/dee8a27ce606f644cef0220deac98e88640d9b16),
published at 2026-08-25 14:32 UTC. The complete release delta is 98 commits and
61 changed files from
[`v0.7.0...v0.8.0`](https://github.com/mixelpixx/Konnect/compare/v0.7.0...v0.8.0).
Current upstream `main` is
[`c68c745`](https://github.com/mixelpixx/Konnect/commit/c68c745c2a26808726a477b2ef8e56e05833bdc0),
one commit ahead of the tag solely to stamp per-platform v0.8.0 PCM metadata.
The authoritative release description is
[v0.8.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.8.0).

At this snapshot the repository has **32 open issues** and **13 open pull
requests**, down from 40 and 26 in the August 21 backlog.

## What v0.8.0 changes

### Released safety and correctness improvements

- [PR #294](https://github.com/mixelpixx/Konnect/pull/294) adds
  `repair_corrupted_footprints`, a dry-run-first, revision-gated repair for the
  footprint-artwork corruption caused by v0.4.0-v0.6.1. The release evidence is
  a real 68-footprint corrupted board with 848 phantom pads repaired in one
  KiCad undo commit.
- [Issue #314](https://github.com/mixelpixx/Konnect/issues/314) fixed
  `set_board_size` appending rather than replacing Edge.Cuts. The fixed live IPC
  path was verified with two consecutive resizes and zero DRC errors.
- [Issue #315](https://github.com/mixelpixx/Konnect/issues/315) exposed that
  `move_connected` never moved wiring. v0.8.0 replaces false success with an
  explicit refusal and removes its dead parameters. The real feature remains
  open and depends on #120.
- [PR #285](https://github.com/mixelpixx/Konnect/pull/285) completes the #251
  parameter-honesty consolidation. Catalogue-wide CI now checks that every
  advertised input reaches an implementation, and inert inputs are documented
  in
  [`docs/API_MIGRATIONS.md`](https://github.com/mixelpixx/Konnect/blob/v0.8.0/docs/API_MIGRATIONS.md).
- [PR #317](https://github.com/mixelpixx/Konnect/pull/317) prevents
  `add_sheet_pin` from making a root schematic unloadable; #307-#313 correct
  no-op sheet edits, sheet-property moves, duplicate UUIDs, text justification,
  project library-table targeting, resolved generated-pin positions, and the
  schematic-view return contract.
- [PR #323](https://github.com/mixelpixx/Konnect/pull/323) consolidates
  schematic connectivity consumers onto one `ConnectivityIndex`; #262 adds
  power-symbol resolution and #267 respects intentional unconnected pins.
- [PR #318](https://github.com/mixelpixx/Konnect/pull/318) makes
  `batch_add_wire` refuse an item missing a coordinate rather than inventing
  `(0,0)`. This closes the wire half of #234; broader malformed nested-input
  protection remains represented by conflicting PR #268.
- [PR #316](https://github.com/mixelpixx/Konnect/pull/316) makes `add_zone`
  edit and refill a live board through IPC when available, returning `source`
  and `zone_id`; the file fallback is explicit.
- [PR #207](https://github.com/mixelpixx/Konnect/pull/207) makes
  `get_board_info` use the live board where possible, and
  [PR #324](https://github.com/mixelpixx/Konnect/pull/324) adds custom User
  paper dimensions.
- [PR #327](https://github.com/mixelpixx/Konnect/pull/327) answers
  `get_datasheet_url` from the local JLCPCB catalogue first and returns the
  catalogue Datasheet field from search results.
- [PR #306](https://github.com/mixelpixx/Konnect/pull/306) ships the developer
  architecture/tool documentation approved in
  [Discussion #301](https://github.com/mixelpixx/Konnect/discussions/301),
  including the maintainer-requested evidence rules and write-path gates.

### Public contract changes the companion must know

The [v0.8.0 release notes](https://github.com/mixelpixx/Konnect/releases/tag/v0.8.0)
record `toolset_count: 19`, 204 registered tools, and 210 total tools.

- New tool: `repair_corrupted_footprints`.
- `get_schematic_view` is now a hard response change: structured JSON with
  `schematic`, `svg`, `bytes`, and `format`, rather than a text note.
- `get_board_info` adds `source` and `paper_size_mm`.
- `add_zone`/`add_copper_pour` add live/file source and zone identity, plus
  optional `name`, `priority`, and `pad_connection` inputs.
- `create_symbol` returns resolved `units[].pins[]`.
- `edit_sheet` and `move_sheet` add `changed`; `set_board_size` adds
  `replaced_segments`.
- ERC/DRC violations retain `rule` and their complete `items` arrays.
- Catalogue queries return datasheet fields.
- Removed inert inputs: `import_sheet_pins.project_name`,
  `refill_zones.zones`, `run_drc.tests`, two `audit_decoupling` inputs,
  `export_manufacturing_package.quantity`,
  `validate_for_manufacturing.schematic`, `estimate_cost.schematic`, and all
  `move_connected` parameters. Exact migrations are in
  [API_MIGRATIONS.md](https://github.com/mixelpixx/Konnect/blob/v0.8.0/docs/API_MIGRATIONS.md).

## Completed items from the August 21 backlog

These 13 formerly open issues are now closed as completed:

| Issue | Released resolution |
| --- | --- |
| [#219](https://github.com/mixelpixx/Konnect/issues/219) | User paper dimensions via #324. |
| [#234](https://github.com/mixelpixx/Konnect/issues/234) | Required nested fields and `batch_add_wire` refusal via #268/#318; #268 itself now needs rebase. |
| [#251](https://github.com/mixelpixx/Konnect/issues/251) | Parameter-honesty consolidation and CI guard via #285. |
| [#255](https://github.com/mixelpixx/Konnect/issues/255) | Local-catalog datasheet lookup via #327. |
| [#286](https://github.com/mixelpixx/Konnect/issues/286) | Text justification via #308. |
| [#287](https://github.com/mixelpixx/Konnect/issues/287) | Sheet captions move with the sheet via #309. |
| [#288](https://github.com/mixelpixx/Konnect/issues/288) | Fresh nested UUIDs on duplication via #310. |
| [#289](https://github.com/mixelpixx/Konnect/issues/289) | Correct project library-table target via #311. |
| [#290](https://github.com/mixelpixx/Konnect/issues/290) | Actual SVG returned via #313. |
| [#292](https://github.com/mixelpixx/Konnect/issues/292) | Idempotent edits via #307. |
| [#293](https://github.com/mixelpixx/Konnect/issues/293) | Resolved pin geometry returned via #312. |
| [#303](https://github.com/mixelpixx/Konnect/issues/303) | Valid sheet-pin rotation via #317. |
| [#304](https://github.com/mixelpixx/Konnect/issues/304) | Actionable pre-6.0 footprint upgrade hint via #319. |

The maintainer's
[status response in Discussion #165](https://github.com/mixelpixx/Konnect/discussions/165#discussioncomment-18149346)
confirms these closures, the validated #294 repair, the #314/#315 honesty fixes,
and that #120, #240/#241, #189, and the Freerouting bridge are the remaining
unclaimed high-priority choices.

## New open risks since the prior snapshot

1. **P0: #326 — a project-wide connectivity hazard.**
   [`create_netclass` omits `wire_width`](https://github.com/mixelpixx/Konnect/issues/326),
   which makes Eeschema refuse or strip junction dots and can break T-connected
   pins. The maintainer confirmed the small implementation surface and requested
   a full KiCad-default-field round-trip test. Despite its “good first issue”
   label, the user impact belongs in P0 because a PCB netclass operation can
   silently alter schematic connectivity across the project.
2. **P0/P1 boundary: #328 — false connectivity findings on bus designs.**
   The new shared index is
   [bus-blind](https://github.com/mixelpixx/Konnect/issues/328), so valid wires
   terminating at bus entries and labels attached to buses are reported
   floating. This does not mutate the design, but it can cause an agent to
   “repair” correct wiring. Treat Konnect connectivity summaries as incomplete
   on bus-using sheets until fixed; KiCad ERC is authoritative.
3. **P1: #329 — result coordinates are reversed.**
   [`add_bus_entry`](https://github.com/mixelpixx/Konnect/issues/329) reports
   its `bus_side` and `wire_side` endpoints backwards. The file is correct but a
   caller following the response wires to the wrong corner.
4. **P1: #325 — some MCP clients cannot reach the catalogue.**
   [VS Code Copilot caps callable tools](https://github.com/mixelpixx/Konnect/issues/325)
   and does not reliably refresh after toolset loading. A working two-tool
   call/help proxy is documented in the issue. The new
   [ROADMAP](https://github.com/mixelpixx/Konnect/blob/v0.8.0/ROADMAP.md)
   adopts a compact-tool-surface mode and MCP tool-directory resources as the
   planned direction. Codex currently avoids this class through eager exposure,
   but the companion must keep the version/tool-count gate and should not assume
   every client shares Codex's behavior.
5. **P1: #315 remains a feature gap.** The released false-success path is gone,
   but connected wire carrying still does not exist. Guidance must use a plain
   move followed by explicit re-routing and ERC, or refuse the requested edit.

## Recommended revised priority order

1. **#326**: restore complete KiCad Default netclass fields before any workflow
   creates or edits netclasses.
2. **#120 + #315**, starting with mergeable green
   [PR #330](https://github.com/mixelpixx/Konnect/pull/330): reconcile junctions
   on move. PR #330 is explicitly only the junction prerequisite, not wire
   stretching, and leaves rotate/delete for later.
3. **#240/#241**: prevent stale-file mutation after an editor/IPC loss and add
   reusable document-answering IPC test coverage.
4. **#182**: finish multi-unit mutation by rebasing #273 onto the shared
   connectivity index.
5. **#189**: bound root/library discovery and fail on ambiguity.
6. **#328/#329**: make the shared connectivity model bus-aware and correct the
   endpoint response before workflows trust bus validation.
7. **Freerouting bridge**: implement the already agreed standalone-JAR,
   DSN/export-route-SES/import design recorded in the
   [roadmap](https://github.com/mixelpixx/Konnect/blob/v0.8.0/ROADMAP.md), with
   separate engine/bridge capability reporting, board identity, and atomic
   import.
8. **#103/#242/#233/#325**: lifecycle, startup mutation, and client-compatible
   tool discovery.
9. Rebase or close the remaining older PRs, then address platform, diagnostics,
   library fidelity, and bounded enhancements.

## Complete current open-issue inventory

| Priority | Issue | Disposition |
| --- | --- | --- |
| P1 | [#84](https://github.com/mixelpixx/Konnect/issues/84) | Finish structural replacement of indentation-sensitive scans. |
| P1 | [#103](https://github.com/mixelpixx/Konnect/issues/103) | Fix orphan server ownership and multi-instance tracking. |
| P2 | [#118](https://github.com/mixelpixx/Konnect/issues/118) | Add a real layer-aware 2-D board plot. |
| P1 | [#119](https://github.com/mixelpixx/Konnect/issues/119) | Bound and consolidate DRC reporting. |
| P0 | [#120](https://github.com/mixelpixx/Konnect/issues/120) | Junction correctness on move/delete; prerequisite for #315. |
| P1 | [#131](https://github.com/mixelpixx/Konnect/issues/131) | Sign/notarize both macOS slices and final artifact. |
| P2 | [#154](https://github.com/mixelpixx/Konnect/issues/154) | Homebrew after stable signed artifacts. |
| P3 | [#181](https://github.com/mixelpixx/Konnect/issues/181) | Preserve lock-name compatibility before `sha2` bump. |
| P0 | [#182](https://github.com/mixelpixx/Konnect/issues/182) | Finish unit-aware mutation after shared-index read path. |
| P0 | [#189](https://github.com/mixelpixx/Konnect/issues/189) | Bound project-root discovery and refuse ambiguity. |
| P2 | [#210](https://github.com/mixelpixx/Konnect/issues/210) | Reduce whole-sheet serialization diff churn. |
| P1 | [#221](https://github.com/mixelpixx/Konnect/issues/221) | Correct live-CI claims and rotation read-back flake. |
| P2 | [#225](https://github.com/mixelpixx/Konnect/issues/225) | Select a footprint graphic by identity, not only layer. |
| P3 | [#226](https://github.com/mixelpixx/Konnect/issues/226) | Resolve placed metadata fidelity with measured impact. |
| P1 | [#231](https://github.com/mixelpixx/Konnect/issues/231) | Live Update Footprints from Library; rebase #232. |
| P1 | [#233](https://github.com/mixelpixx/Konnect/issues/233) | Client fails to refresh dynamically loaded Linux toolset. |
| P0 | [#240](https://github.com/mixelpixx/Konnect/issues/240) | Refuse stale fallback after observed-live IPC loss. |
| P2 | [#241](https://github.com/mixelpixx/Konnect/issues/241) | Shared open-document refusal mock. |
| P1 | [#242](https://github.com/mixelpixx/Konnect/issues/242) | Stop reinstalling guidance as an MCP startup side effect. |
| P0 | [#252](https://github.com/mixelpixx/Konnect/issues/252) | Verify every reported snapshot/package artifact. |
| P1 | [#254](https://github.com/mixelpixx/Konnect/issues/254) | Discover per-user Windows KiCad installations. |
| P1 | [#256](https://github.com/mixelpixx/Konnect/issues/256) | Open and prove a requested PCB editor document. |
| P1 | [#257](https://github.com/mixelpixx/Konnect/issues/257) | Prepare for KiCad 11 SWIG removal/IPC changes. |
| P1 | [#258](https://github.com/mixelpixx/Konnect/issues/258) | Allow explicit custom-field upsert in batch schematic edits. |
| P1 | [#291](https://github.com/mixelpixx/Konnect/issues/291) | Honor or reject requested schematic SVG filename. |
| P2 | [#296](https://github.com/mixelpixx/Konnect/issues/296) | Advanced symbol/footprint generation in agreed focused PRs. |
| P2 | [#305](https://github.com/mixelpixx/Konnect/issues/305) | Add or deliberately route placed-footprint 3-D model editing. |
| P1 | [#315](https://github.com/mixelpixx/Konnect/issues/315) | Build real connected move after #120; refusal is now honest. |
| P1 | [#325](https://github.com/mixelpixx/Konnect/issues/325) | Compact surface/resource directory for capped MCP clients. |
| P0 | [#326](https://github.com/mixelpixx/Konnect/issues/326) | Restore `wire_width` and full KiCad Default netclass fields. |
| P1 | [#328](https://github.com/mixelpixx/Konnect/issues/328) | Make shared connectivity bus/bus-entry aware. |
| P1 | [#329](https://github.com/mixelpixx/Konnect/issues/329) | Correct swapped bus-entry response endpoints. |

## Complete current open-PR inventory

States are live at the snapshot; a conflict means “rebase required,” not a
quality verdict.

| PR | Current state | Assessment |
| --- | --- | --- |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) | Conflicting | Stale reload-server design; likely supersede or rework for #103/#242. |
| [#232](https://github.com/mixelpixx/Konnect/pull/232) | Conflicting | Rebase and repeat real-KiCad footprint-refresh evidence. |
| [#243](https://github.com/mixelpixx/Konnect/pull/243) | Mergeable, green | Small Actions dependency update. |
| [#264](https://github.com/mixelpixx/Konnect/pull/264) | Conflicting | Atomic placement batch remains useful after rebase/design confirmation. |
| [#265](https://github.com/mixelpixx/Konnect/pull/265) | Draft, conflicting | Rebase its pad-read hardening delta over merged #207. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) | Conflicting | Retain malformed nested-input coverage not already landed in #318/#285. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) | Conflicting | Rebase and reduce to unresolved #252 artifact verification. |
| [#273](https://github.com/mixelpixx/Konnect/pull/273) | Conflicting | Rebase multi-unit mutation over #323 as roadmap directs. |
| [#275](https://github.com/mixelpixx/Konnect/pull/275) | Conflicting | Rebase symbol-geometry measurement after unit-aware work. |
| [#320](https://github.com/mixelpixx/Konnect/pull/320) | Mergeable, green | Viewer `uuid` patch update. |
| [#321](https://github.com/mixelpixx/Konnect/pull/321) | Mergeable, green | Workspace `uuid` patch update. |
| [#322](https://github.com/mixelpixx/Konnect/pull/322) | Mergeable, Windows CI failing | Structural library-field read is useful, but not ready until Windows is green. |
| [#330](https://github.com/mixelpixx/Konnect/pull/330) | Mergeable, green | High-priority #120 prerequisite; review stray `.DS_Store` and preserve its explicit partial scope. |

## Implications for `konnect-codex`

### Required synchronization

1. Bump the companion compatibility/version gate, README badge and commands,
   release notes, Cargo version, policy baseline, enhancement metadata, and
   release/tag from 0.7.0 to 0.8.0. Pin the reviewed upstream tag commit
   `dee8a27`, while noting the one metadata-only main commit separately.
2. Rebuild the upstream baseline from the v0.8.0 Claude assets. Only three
   upstream skill files changed from v0.7.0:
   - `kicad-manufacture`: removes the inert export `quantity` and estimate
     `schematic` examples;
   - `kicad-pcb`: documents live IPC zone creation, source/warning behavior,
     and zone `name`/`priority`/`pad_connection`;
   - `konnect`: narrows the integration description from Freerouting operation
     to Freerouting installation checks.
   No upstream agent file changed. Preserve companion-owned overlays according
   to the enhancement/change policy rather than recopying the Claude files.
3. Remove `autoroute` from the companion MCP hook matcher and tests that treat
   it as a Konnect tool. Keep “autoroute” as a user-intent keyword and keep the
   companion's separate Freerouting bridge; the distinction must be explicit.
4. Update guidance and tests for the structured `get_schematic_view` result,
   new tool/response fields, and every schema removal in API_MIGRATIONS. No
   skill or agent should call `move_connected` until the real feature lands.
5. Add temporary v0.8.0 safety guidance:
   - do not create/overwrite Default netclasses with Konnect until #326 is
     fixed, or prove `wire_width` and re-run KiCad ERC/junction checks;
   - treat Konnect orphan/connectivity results as incomplete on bus sheets
     until #328, and use KiCad ERC as authority;
   - do not trust the named bus-entry response corners until #329;
   - after a plain component move, explicitly repair wiring and run ERC;
   - use `repair_corrupted_footprints` dry-run + returned revision only for
     boards exhibiting the documented legacy signature.
6. Retain companion Freerouting support. v0.8.0 intentionally removed the fake
   Konnect tool and the roadmap adopts the standalone-JAR bridge as the official
   direction; the companion implementation remains additive, not conflicting.
7. Keep eager toolsets for Codex, but add a compatibility note that #325 is a
   different client class. Do not add a generic proxy to the Codex companion
   unless Codex itself exhibits the cap.

### Verification before publishing the companion

- Unit tests, formatting and Clippy for the companion, plus install/uninstall
  and version-mismatch tests against exactly Konnect 0.8.0.
- Confirm installed Codex skills/agents/hooks are the v0.8.0 baseline plus only
  declared companion enhancements; verify no `autoroute` MCP hook remains.
- Start/stop/restart the installed MCP server and verify scoped child-process
  cleanup without killing unrelated instances.
- Run a compact smoke test for `get_schematic_view`, `get_board_info`, live
  `add_zone`, local datasheet lookup, and the removed-argument behavior.
- Run the full konnect-codex end-to-end benchmark requested by the roadmap,
  including direct KiCad parse/ERC/DRC, connectivity and inventory evidence,
  placement images, Freerouting provenance, post-import inventory, 3-D review,
  and manufacturing artifacts. Include a bus design and a Default-netclass
  probe so #326/#328/#329 cannot hide behind the happy path.

## Backlog/discussion rewrite guidance

The next Discussion #165 body should be titled for **v0.8.0** and use the
current 32-issue/13-PR inventory above. It should:

- replace the old “what changed since August 17/21” sections with the released
  v0.8.0 safety/correctness summary;
- remove all 13 completed issues from active priorities while crediting their
  released PRs;
- promote #326 to the top P0 position and add #328/#329/#325/#315;
- retain #120, #182, #189, #240, #252 and their dependency relationships;
- assess #330 as a partial #120 prerequisite, not a complete connected move;
- record that the Freerouting bridge is now an agreed roadmap item even though
  #253 is closed and no Konnect `autoroute` tool exists;
- preserve the contribution rule from ROADMAP/CONTRIBUTING: claim work on its
  issue, agree on design first, then submit one focused PR; and
- commit to a v0.8.0 companion benchmark, because the roadmap explicitly makes
  an end-to-end benchmark part of the minor-release rhythm.
