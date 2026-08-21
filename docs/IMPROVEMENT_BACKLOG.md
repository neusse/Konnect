> **Disclosure:** I used OpenAI Codex to re-evaluate Konnect and prepare this
> improvement backlog. The evaluation used the current repository source and
> documentation, hands-on use of Konnect on a real KiCad 10 project, the
> [konnect-codex plugin](https://github.com/neusse/konnect-codex), discussions
> [#152](https://github.com/mixelpixx/Konnect/discussions/152),
> [#224](https://github.com/mixelpixx/Konnect/discussions/224), and
> [#239](https://github.com/mixelpixx/Konnect/discussions/239), every currently
> open issue and its comments, every open pull request, and the issues and pull
> requests closed since the prior snapshot.
>
> This is a prioritization proposal, not a maintainer commitment. I plan to
> work on an approved high-priority item by following the roadmap and
> contribution process: discuss the design first, then submit one focused,
> reviewable pull request.

# Konnect improvement backlog

This snapshot is current as of **August 17, 2026**, against upstream `main` at
[`59d0ead`](https://github.com/mixelpixx/Konnect/commit/59d0ead907b4f4b1d87bd2c35b9166039990a16e).
At the time of review, the repository has **34 open issues** and **7 open pull
requests**. The linked issue or pull request is authoritative if its state
changes after this snapshot.

## Contribution guardrails

All implementation should follow
[`CONTRIBUTING.md`](https://github.com/mixelpixx/Konnect/blob/main/CONTRIBUTING.md),
[`ROADMAP.md`](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md), and
[`NAMING_CONVENTIONS.md`](https://github.com/mixelpixx/Konnect/blob/main/docs/NAMING_CONVENTIONS.md):

- Discuss non-trivial work before implementation and keep each PR to one
  reviewable outcome.
- Treat MCP tools, schemas, config keys, paths, flags, and response fields as
  public API. Preserve compatibility or document a migration.
- State the user-visible problem, root cause, design, compatibility effects,
  validation, risk, and rollback behavior.
- Read required arguments through the repository helpers. Nested array items
  need equally explicit validation.
- Run the locked workspace tests and doctests, Clippy, and formatting checks.
  When tools change, update and verify every registry and documentation count.
- Keep generated output, personal configuration, downloaded catalogs, and
  unrelated cleanup out of a contribution.

## What changed since the August 15 snapshot

The project moved from `e8fbadf` to `59d0ead`, through releases v0.4.0,
v0.4.1, v0.5.0, v0.5.1, v0.6.0, and v0.6.1 plus eight post-release commits.
Several former priorities are complete and should not remain in the active
backlog:

- Multi-client installer guidance and corrected bundled skills landed through
  #217, #223, and related commits. First-class Codex behavior is now best kept
  in the independent
  [konnect-codex plugin](https://github.com/neusse/konnect-codex); the remaining
  Konnect-side problem is the startup mutation in #242.
- Hierarchical schematic instance identity (#204), truthful symbol-library
  registration (#211), skill parameter guards (#183), and structured path
  argument errors (#194) are fixed.
- Back-side and closed-board move, rotate, and flip support closed #115 through
  PRs #229 and #230.
- Top-level required arguments are enforced (#218), while #234 correctly keeps
  the unresolved nested-array version separate.
- The KiCad crash caused by unsupported `Dwgs.User` layer serialization is fixed
  in v0.6.1 (#237). The `--help` installer side effect is also fixed (#238).
- Board-footprint graphic editing over IPC landed through #160. Junction
  pruning after wire deletion landed through #214, narrowing but not closing
  #120.
- Post-v0.6.1 `main` fixes the benchmark's phantom-pad sync defect (#244),
  reports all KiCad DRC result arrays (#245), counts actual pads in reviews
  (#246), and refuses manufacturing approval without DRC evidence (#247).
- The post-release sync commits `222771c` and `59d0ead` add exact sent-item
  read-back checks and narrow benign mismatches. They directly target the
  update failure seen in discussion #239, but the full benchmark has not yet
  been rerun against this head, so they are progress rather than qualification.
- Commit `f6bfb37` corrects the false statement that KiCad 10 removed Specctra
  commands. It does not make the advertised `autoroute` handler operational;
  #253 remains open.

## P0 — possible design damage, unsafe fallback, or false manufacturing truth

### 1. Finish multi-unit schematic correctness

[Issue #182](https://github.com/mixelpixx/Konnect/issues/182) remains the
highest-risk active schematic item. Mutators, validators, exporters, analysis,
design review, and annotation paths still resolve some shared references
through unit 1. A move or rotation can tear a logical part apart, a delete can
leave other units orphaned, and analysis can report the wrong connectivity.

Recommended direction:

- Fix the mutating `sch_components` paths first, using the established
  `find_all_symbol_instance_blocks` and unit-aware pin helpers.
- Keep reporting and analysis changes in a separate focused PR if necessary.
- Test two units with pins at the same local coordinate but different placed
  transforms, so a unit-1 substitution is observable.
- Require every remaining first-instance lookup to become unit-aware or to
  document why unit 1 is intentionally correct.

### 2. Recompute connectivity when objects move

[Issue #120](https://github.com/mixelpixx/Konnect/issues/120) remains open after
#214. Moving a pin onto the middle of a wire can leave it electrically
unconnected; moving it away can strand a junction that later shorts a crossing.
`batch_delete` also bypasses the new wire-deletion pruning path.

Reuse `prune_orphaned_junctions` and the established mid-wire detection at the
old and new coordinates. Settle whether generated junctions should remain
mid-segment or use KiCad's canonical split-wire form before expanding the
mutation model. Test move-on, move-off, T-junction, unrelated crossing, label
movement, and batch deletion with ERC and a KiCad reload as independent
witnesses.

### 3. Reject malformed nested inputs before any write

[Issue #234](https://github.com/mixelpixx/Konnect/issues/234) shows that nested
`required` fields are still defaulted. `batch_add_wire` can turn `{}` into a
successful `(0,0)` to `(0,0)` wire, `create_footprint` can synthesize a plausible
pad at the origin, and `create_symbol` can create a pinless unit.

Validate array items with indexed structured errors. Creation of one artifact
should fail atomically. For true batch tools, choose and document either whole
batch refusal or skip-and-report; do not silently manufacture values the caller
never supplied. Add a schema/handler contract guard that descends through array
items so this class cannot return elsewhere.

### 4. Do not edit a stale board immediately after the editor disappears

[Issue #240](https://github.com/mixelpixx/Konnect/issues/240) identifies a gap
in the closed-board fallback. `Unreachable` cannot distinguish “KiCad was never
running” from “KiCad just crashed while holding this board with unsaved work.”
The next call can edit the stale file and reassure the caller that KiCad will
show the change later.

Remember boards observed live during the server lifetime and refuse a file
fallback after that editor becomes unreachable. Evaluate KiCad lock files as
additional evidence, but do not make a stale lock the only authority. Tighten
the warning even if stronger detection lands later. The invariant is that a
fallback must not silently win over or compound lost editor state.

### 5. Make export and manufacturing responses describe results, not requests

Three issues form one high-risk contract cluster but should remain focused PRs:

- [#251](https://github.com/mixelpixx/Konnect/issues/251): position-file units
  and side and Gerber layers are accepted and echoed without being applied.
- [#252](https://github.com/mixelpixx/Konnect/issues/252): `snapshot_project`
  discards a PCB export error and returns an artifact path it never verified;
  the same verification principle applies to manufacturing packages.
- [#250](https://github.com/mixelpixx/Konnect/issues/250): PDF/SVG pass repeated
  `--layers` flags where KiCad 10 requires one comma-separated value, and SVG
  relies on a changing implicit mode.

Fix the wrappers, verify that every reported artifact exists and is non-empty,
and include actionable argv context when `kicad-cli` exits without stderr. Add
cross-cutting tests that schemas are actually consumed and response claims are
derived from observed results. A manufacturing workflow must fail closed rather
than return a plausible package summary for incomplete or differently
parameterized output.

### 6. Bound project discovery before it selects the wrong libraries

[Issue #189](https://github.com/mixelpixx/Konnect/issues/189) still allows an
unbounded ancestor walk when the target directory has neither a project nor a
library table. It can silently select an unrelated ancestor project and resolve
`${KIPRJMOD}` against the wrong root.

Prefer explicit project context. When discovery is genuinely ambiguous, return
a structured error naming the candidates rather than choosing one. Preserve
deep legitimate sheet hierarchies and document the boundary rule; an arbitrary
depth limit only relocates the failure.

## P1 — core workflow reliability and truthful diagnostics

### 7. Use one connectivity model for orphan detection

[Issue #249](https://github.com/mixelpixx/Konnect/issues/249) explains why
`find_orphan_items` reported all 35 legal pin-mounted labels as floating while
ERC and every other connectivity check passed. The checker only compares labels
with wire endpoints and never resolves pins. An attempted workaround created a
real CC2-to-GND short, illustrating why contradictory validators are dangerous.

Reuse the existing `NetGraph`, pin extraction, and placed-unit transforms. Then
either implement the promised unconnected-pin check or narrow the tool
description. ERC remains the authoritative external check.

### 8. Replace the remaining indentation-sensitive scans

[Issue #84](https://github.com/mixelpixx/Konnect/issues/84) now covers
`sch_export`, `integration`, `schematic_builder`, and a `library.rs` pad count.
The last one is also filed as the user-visible
[#248](https://github.com/mixelpixx/Konnect/issues/248): standard KiCad CRLF,
tab-indented footprints report `pad_count: 0`.

Use the existing structural S-expression helpers, not whitespace literals.
Test tabs, spaces, CRLF, LF, compact input, quoted strings, and insertion at the
last top-level node. Keep this distinct from #210, whose remaining problem is
format fidelity rather than node selection.

### 9. Make Windows installation discovery reflect real KiCad installs

[Issue #254](https://github.com/mixelpixx/Konnect/issues/254) confirms that both
binary and library discovery omit per-user Windows installs under
`%LOCALAPPDATA%\Programs\KiCad`. Binary and library searches already have
different hardcoded lists.

Unify discovery, prefer authoritative KiCad configuration or Windows uninstall
registry data, then fall back to documented paths. Cover symbols, footprints,
3D models, and binaries together and report unresolved roots. This may also
explain missing STEP/3D bodies seen during the benchmark.

### 10. Open the requested editor document, not merely the project manager

[Issue #256](https://github.com/mixelpixx/Konnect/issues/256) shows that
`launch_kicad_ui` opens the project manager and waits for any IPC endpoint; it
cannot ensure a requested board is open and active. Add a document-targeted
operation that reaches and reports the states “process running,” “IPC ready,”
“PCB Editor running,” “requested board open,” and “requested board active.” If
KiCad cannot reach a state without user action, return the precise manual step
instead of reporting generic launch success.

### 11. Restore a truthful Freerouting capability

[Issue #253](https://github.com/mixelpixx/Konnect/issues/253) now tracks the
advertised-but-disabled `autoroute` tool and incomplete JAR discovery.
Freerouting can run standalone, while the KiCad ActionPlugin is workflow glue
for DSN export, routing, SES import, and editor refresh. Installing either does
not currently enable Konnect autorouting.

Keep two capabilities explicit: **Freerouting engine found** and **KiCad
DSN/SES bridge available**. Prefer an optional-plugin architecture: discover an
explicit or standalone JAR and, when useful, the JAR bundled by KiCad PCM, but
implement the editor-side bridge through a stable in-editor API. Validate board
identity, preserve netclass widths, import atomically, refresh the editor, and
report changed routes plus remaining unrouted connections. Driving the
ActionPlugin is a viable alternative, but makes that plugin a runtime
dependency and couples Konnect to its installation and interface.

### 12. Keep guidance installation explicit and durable

[Issue #242](https://github.com/mixelpixx/Konnect/issues/242) remains after
v0.6.1: ordinary MCP startup silently reinstalls guidance whenever its marker
is absent, so `uninstall` is reversed on the next start. Server startup should
not mutate Claude or Codex configuration. Prefer explicit `konnect init
--client ...`; if compatibility requires first-run installation, provide a
durable suppression state and a server flag. This also allows
konnect-codex to remain the sole Codex guidance provider without release drift
being overwritten at runtime.

### 13. Diagnose Linux dynamic-tool exposure separately from KiCad IPC

[Issue #233](https://github.com/mixelpixx/Konnect/issues/233) reports that
`load_toolset` returns all 17 `sch_components` tools on Kubuntu and Claude
Desktop, but later calls say “Tool not found.” Because the starter tools remain
available, this may be a client tool-list refresh problem rather than KiCad IPC.

Reproduce with raw MCP over stdio and record `tools/list` before and after
`load_toolset`; then compare Claude Desktop on the same server. A successful
load response must not imply client exposure unless the subsequent tool list
contains the tools. Keep the separately reported custom-library resolution
problem out of the same fix unless the reproduction proves a shared cause.

### 14. Finish high-value PCB state and library workflows already in review

- [Issue #231](https://github.com/mixelpixx/Konnect/issues/231) and
  [PR #232](https://github.com/mixelpixx/Konnect/pull/232) add dry-run,
  revision-gated, atomic live “Update Footprints from Library.” The PR is large
  but focused, CI-green, and carries a disposable KiCad acceptance test. Review
  fail-closed unsupported-content handling and the composition with v0.6.1's
  layer validation before merge.
- [PR #207](https://github.com/mixelpixx/Konnect/pull/207) makes board info and
  pad reads prefer the named live board and report the source. It is now ready
  and CI-green. The remaining explicit limitation is lack of real-KiCad
  verification for the empty-pad response shape.
- [Issue #258](https://github.com/mixelpixx/Konnect/issues/258) should give
  `batch_edit_schematic_components` explicit, default-safe create-missing
  semantics, reuse the annotation helpers, report created versus updated
  fields, and preserve multi-unit behavior.

### 15. Complete diagnostic, lifecycle, data, and platform reliability

- [#119](https://github.com/mixelpixx/Konnect/issues/119): bound
  `get_drc_violations`, report totals consistently, and handle its output parent
  directory with a structured contract.
- [#103](https://github.com/mixelpixx/Konnect/issues/103): finish server-side
  lifecycle ownership for KiCad's direct exec path without killing independent
  MCP-client processes.
- [#255](https://github.com/mixelpixx/Konnect/issues/255): return the local
  catalog's `Datasheet` column before attempting the live LCSC API and expose it
  from part lookup results.
- [#257](https://github.com/mixelpixx/Konnect/issues/257): plan the KiCad 11
  removal of SWIG `pcbnew` before it ships; treat deprecated net codes and
  unstable action strings as watch items, not invented deadlines.
- [#131](https://github.com/mixelpixx/Konnect/issues/131): sign both macOS slices
  and the final universal binary, verify a designated requirement, and move to
  Developer ID signing/notarization for continuity across releases.

## P2/P3 — bounded enhancements, tests, and maintenance

- [#260](https://github.com/mixelpixx/Konnect/issues/260) shows that model and
  workflow guidance materially affect board quality. Document a recommended
  qualification flow and link non-Claude users to compatible guidance such as
  konnect-codex, without promising that any model produces an orderable board.
- [#222](https://github.com/mixelpixx/Konnect/issues/222) already has
  CI-green [PR #259](https://github.com/mixelpixx/Konnect/pull/259), adding the
  missing `get_netclasses` read path with explicit saved-file provenance.
- [#118](https://github.com/mixelpixx/Konnect/issues/118): keep the useful 3-D
  preview and add a separate layer-aware SVG/2-D plot, after #250 fixes the
  underlying SVG wrapper.
- [#225](https://github.com/mixelpixx/Konnect/issues/225): allow
  `set_footprint_graphics` to select one library graphic by `item_id`; refuse
  modes that make no sense for an item selector.
- [#210](https://github.com/mixelpixx/Konnect/issues/210) is substantially fixed.
  The remaining churn is KiCad's width-based packing of `(pts ...)`; prefer
  targeted edits or an evidence-based wrapping implementation.
- [#221](https://github.com/mixelpixx/Konnect/issues/221): correct the nonexistent
  live-GUI CI claim, provide a named-net fixture, and diagnose the intermittent
  rigid-body transform read-back test.
- [#241](https://github.com/mixelpixx/Konnect/issues/241): extract a reusable IPC
  mock that can answer `GetOpenDocuments` and cover the load-bearing refusal
  branch for every closed-board writer.
- [#219](https://github.com/mixelpixx/Konnect/issues/219): report custom board
  paper dimensions without changing the existing `paper` field.
- [#226](https://github.com/mixelpixx/Konnect/issues/226): determine through
  KiCad and BOM behavior whether empty Datasheet and absent Description on a
  placed symbol have any consumer-visible effect before changing the writer.
- [#154](https://github.com/mixelpixx/Konnect/issues/154): add a Homebrew tap only
  after #131 establishes stable macOS artifact identity.
- [#181](https://github.com/mixelpixx/Konnect/issues/181): pin the existing
  document-lock filename for a fixed input, then upgrade `sha2` with byte-identical
  lowercase hex output.

## Open pull-request assessment

This describes review state at the snapshot; it is not merge approval.

| PR | Current state | Backlog assessment |
| --- | --- | --- |
| [#259](https://github.com/mixelpixx/Konnect/pull/259) `get_netclasses` | Ready, mergeable, CI green | Directly closes #222. Good saved-file provenance, KiCad 10 net parsing, overlapping-class semantics, and complete tool-count updates. |
| [#243](https://github.com/mixelpixx/Konnect/pull/243) setup-python v7 | Ready, mergeable, CI green | One-line Node 24-compatible CI dependency update; keep separate from product priorities. |
| [#236](https://github.com/mixelpixx/Konnect/pull/236) hermetic symbol tests | Ready, mergeable, approved, CI green | Corrects three tests that accidentally resolve the machine's real Device library. Small, valuable developer-gate fix. |
| [#235](https://github.com/mixelpixx/Konnect/pull/235) create-symbol datasheet | Ready, mergeable, CI green | Adds an explicit datasheet argument and prevents the `~` placeholder from recreating a library-copy mismatch. Related to, but does not close, #226 or #255. |
| [#232](https://github.com/mixelpixx/Konnect/pull/232) update footprints from library | Ready; GitHub mergeability currently unresolved; CI green | Large focused implementation for #231 with dry-run/revision safety and live acceptance evidence. Review unsupported-content boundaries and current-main composition carefully. |
| [#207](https://github.com/mixelpixx/Konnect/pull/207) live board and pad reads | Ready, mergeable, CI green | High-value correction for unsaved state and wrong-board reads. Real KiCad verification of the empty-pad response remains explicitly unperformed. |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) `reload_server` | Stale; requested rework not supplied | Preserve argv, restrict to stdio, stop accepting requests before exec, and do not advertise an always-failing Windows tool. Close or transfer ownership if the author does not resume. |

## Complete open-issue disposition

| Issue | Priority | Current disposition |
| --- | --- | --- |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) indentation-sensitive scans | P1 | Structural parsing sweep; coordinate with #248 and test CRLF. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) orphan servers | P1 | Plugin half is fixed; direct exec path still needs server-owned lifecycle records. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) true 2-D output | P2 | Add a distinct layer plot after #250 repairs SVG export. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) unbounded DRC output | P1 | Bound results and make report-path handling structured. |
| [#120](https://github.com/mixelpixx/Konnect/issues/120) junctions after moves | P0 | Electrical correctness; #214 supplied pruning machinery but not move coverage. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) macOS signing | P1 | Functional TCC/release identity defect and roadmap item. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) Homebrew | P2 | Sequence after stable signed artifacts. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) `sha2` update | P3 | Pin lock-name compatibility before the dependency bump. |
| [#182](https://github.com/mixelpixx/Konnect/issues/182) unit-blind paths | P0 | Highest active schematic correctness priority. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) project-root walk | P0 | Prevent silent selection of unrelated project libraries. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) schematic diff churn | P2 | Substantially fixed; only `(pts ...)` wrapping remains. |
| [#219](https://github.com/mixelpixx/Konnect/issues/219) custom paper dimensions | P3 | Incomplete read result; no data loss. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) live test claims/fixture/flake | P2 | Correct docs and make the manual live gate trustworthy. |
| [#222](https://github.com/mixelpixx/Konnect/issues/222) read netclasses | P2 | PR #259 is ready and CI green. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) select one library graphic | P2 | Extend the existing selector with `item_id`. |
| [#226](https://github.com/mixelpixx/Konnect/issues/226) placed Datasheet/Description | P3 | Confirm a consumer-visible effect before changing output. |
| [#231](https://github.com/mixelpixx/Konnect/issues/231) update footprints from library | P1 | PR #232 implements the requested safe live workflow. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) Linux loaded tools unavailable | P1 | Reproduce at raw MCP and client layers before assigning cause. |
| [#234](https://github.com/mixelpixx/Konnect/issues/234) nested required defaults | P0 | Prevent synthetic wires, pads, and units from malformed input. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) fallback after editor death | P0 | Refuse stale-file fallback after a board was observed live. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) untested open-board refusal | P2 | Shared IPC mock and byte-identical refusal tests. |
| [#242](https://github.com/mixelpixx/Konnect/issues/242) startup reinstalls guidance | P1 | Make server startup non-mutating or persist explicit suppression. |
| [#248](https://github.com/mixelpixx/Konnect/issues/248) footprint pad count zero | P1 | User-visible #84 site; replace whitespace counting structurally. |
| [#249](https://github.com/mixelpixx/Konnect/issues/249) pin-blind orphan checker | P1 | Reuse the same pin-aware net graph as other validators. |
| [#250](https://github.com/mixelpixx/Konnect/issues/250) broken PDF/SVG layers | P0 | Manufacturing/export blocker within the P0 truthfulness cluster. |
| [#251](https://github.com/mixelpixx/Konnect/issues/251) ignored parameters | P0 | Never echo units, side, or layers that were not applied. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) unverified snapshot paths | P0 | Verify artifacts before returning or approving them. |
| [#253](https://github.com/mixelpixx/Konnect/issues/253) disabled autoroute | P1 | Separate engine discovery from the missing KiCad bridge. |
| [#254](https://github.com/mixelpixx/Konnect/issues/254) per-user Windows KiCad | P1 | Unify binary/library/3D discovery using authoritative locations. |
| [#255](https://github.com/mixelpixx/Konnect/issues/255) local datasheet ignored | P1 | Query and expose the local catalog before network fallback. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) cannot open requested board | P1 | Add document-targeted launch/readiness semantics. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) KiCad compatibility watch | P1 | Plan the KiCad 11 SWIG removal; keep softer items as watches. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) batch fields cannot be created | P1 | Add explicit create-missing/upsert semantics with detailed results. |
| [#260](https://github.com/mixelpixx/Konnect/issues/260) recommended MCP workflow | P2 | Document qualification and compatible client guidance without model guarantees. |

## Recommended execution order

1. Fix nested input validation (#234) and the export/manufacturing truth cluster
   (#250, #251, #252) as separate focused PRs.
2. Fix the mutating subset of multi-unit correctness (#182).
3. Close the stale-editor fallback gap (#240) and then add its shared refusal
   tests (#241).
4. Complete move-time connectivity (#120) and unify orphan detection (#249).
5. Replace indentation-sensitive scans (#84/#248) and bound project discovery
   (#189).
6. Land the ready, bounded PRs #236, #235, #259, and #207 after review; review
   the larger #232 independently.
7. Improve Windows discovery (#254), board opening (#256), local datasheets
   (#255), batch field creation (#258), and bounded DRC (#119).
8. Agree on the Freerouting bridge (#253), make guidance startup durable
   (#242), and reproduce Linux tool exposure (#233).
9. Plan the KiCad 11 plugin transition (#257) and macOS signing (#131) before
   release deadlines make them emergencies.
10. Rerun the complete konnect-codex benchmark against current `main` after the
    P0 transfer/export fixes land, preserving the same stop conditions and
    independent KiCad/ERC/DRC/manufacturing witnesses.

This ordering favors bounded changes that prevent silent damage or false
success, then restores the end-to-end workflow, and only then expands the tool
surface.
