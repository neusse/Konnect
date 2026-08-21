# KiCAD-MCP-Server schematic-to-PCB synchronization research

Research date: 2026-08-14  
Sibling repository revision reviewed: [`91189c59ee492bfa7401abf4532d381e32b977ac`](https://github.com/mixelpixx/KiCAD-MCP-Server/commit/91189c59ee492bfa7401abf4532d381e32b977ac)  
Konnect proposal compared: [issue #187, “Add atomic `update_pcb_from_schematic` workflow”](https://github.com/mixelpixx/Konnect/issues/187)

## Executive conclusion

KiCAD-MCP-Server is strong precedent for **the capability and its place in the workflow**, but not for copying its implementation into Konnect.

The sibling project already exposes `sync_schematic_to_board` as the required schematic-to-layout handoff and describes it as the equivalent of KiCad's F8 “Update PCB from Schematic” operation. Its public TypeScript tool forwards to a Python worker, where a SWIG `pcbnew` handler reconstructs connectivity, invokes `kicad-cli` for a component list, loads missing footprints, assigns pad nets, and saves the board. The repository itself now describes Konnect as its Rust, official-IPC successor, while the older server remains Python/TypeScript and SWIG-based ([README, lines 5–14](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/README.md#L5-L14)).

That history supports approving Konnect issue #187, especially these choices:

1. keep one high-level public operation;
2. preserve board-only footprints by default;
3. obtain the complete component/connectivity model from KiCad rather than recreating it geometrically;
4. stage new footprints somewhere useful instead of piling them at `(0, 0)`;
5. add dry-run, stale-plan rejection, and one IPC commit in Konnect, because the sibling operation has none of those safeguards.

The most consequential negative evidence is current and first-party:

- matching only by reference is an acknowledged open defect ([issue #250](https://github.com/mixelpixx/KiCAD-MCP-Server/issues/250));
- an open fix reports that the current connectivity reconstruction silently drops unlabeled nets ([PR #358](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/358));
- the handler has no dry-run, plan revision, rollback, or IPC transaction;
- skipped/unresolvable footprints and failed `kicad-cli` extraction can still produce an overall success response;
- board-only preservation and `(0, 0)` staging were explicit design decisions in the merged footprint-add work, with better staging left for later ([PR #171](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/171)).

The right use of this research is therefore **process precedent and failure evidence**, not code reuse.

## End-to-end layered process

The sibling operation crosses several layers:

| Layer | What happens | Evidence |
|---|---|---|
| MCP/TypeScript tool | Registers `sync_schematic_to_board`, requires `schematicPath` and `boardPath`, forwards both, and returns the Python result as formatted JSON text. | [`src/tools/schematic.ts`, lines 1574–1587](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/tools/schematic.ts#L1574-L1587) |
| Node-to-Python bridge | Starts a long-lived KiCad Python subprocess, queues a newline-delimited JSON command, and waits for one response. | [`src/server.ts`, lines 503–530](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/server.ts#L503-L530), [`src/server.ts`, lines 721–747](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/server.ts#L721-L747), and [`src/server.ts`, lines 880–918](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/server.ts#L880-L918) |
| Python router | Maps the command to `_handle_sync_schematic_to_board`. The generic dispatcher prefers IPC only for commands in `IPC_CAPABLE_COMMANDS`; sync is not in that table, so it follows the SWIG/file path even when IPC is connected. | [`python/kicad_interface.py`, lines 630–632](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L630-L632), [`python/kicad_interface.py`, lines 709–741](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L709-L741), and [`python/kicad_interface.py`, lines 964–1044](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L964-L1044) |
| Board acquisition | Loads the requested `.kicad_pcb` via SWIG or uses the worker's current in-memory board; if no schematic was supplied, it guesses a sibling file and then the first schematic in the directory. | [`python/commands/schematic_handlers.py`, lines 2889–2940](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2889-L2940) |
| Connectivity model | Recursively lists every `.kicad_sch` file under the project directory, parses each with `kicad-skip`, builds wire adjacency, propagates label names by BFS, and locates symbol pins geometrically. | [`python/commands/schematic_handlers.py`, lines 2748–2887](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2748-L2887) |
| Component model | Separately runs `kicad-cli sch export netlist --format kicadxml` and extracts only reference, value, and footprint. Any CLI absence, nonzero exit, parse error, or other exception becomes an empty component list. | [`python/commands/schematic_handlers.py`, lines 3019–3076](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3019-L3076) |
| Footprint loading | Compares schematic references to existing board references, resolves `Library:Name` through `fp-lib-table`, loads one prototype per distinct footprint, clones it, sets reference/value/FPID, places it at `(0, 0)`, and adds it to the board. | [`python/commands/schematic_handlers.py`, lines 3135–3238](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3135-L3238) |
| Net mutation and save | Adds absent named nets, assigns mapped nets to matching `(reference, pad number)` pairs, records unmatched pads, and directly saves the board. | [`python/commands/schematic_handlers.py`, lines 2942–3008](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2942-L3008) |

There is also a Python-native MCP schema, but it is another exposure of the same handler rather than a separate synchronization engine. Its schema makes both paths optional, unlike the TypeScript wrapper ([`python/schemas/tool_schemas.py`, lines 2511–2527](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/schemas/tool_schemas.py#L2511-L2527)). This duplicated public contract is one example of layering that Konnect's single Rust tool definition can avoid.

## Actual synchronization semantics

### Inputs and outputs

The main TypeScript interface accepts only:

- `schematicPath`;
- `boardPath`.

There is no `dry_run`, expected revision, removal option, placement policy, or conflict policy. The successful Python response returns counts and lists:

- nets added and total names found;
- pads assigned;
- a ten-item sample of unmatched pads;
- footprints added;
- footprints skipped.

The top-level status is still `success: true` when `footprints_skipped` is nonempty ([`python/commands/schematic_handlers.py`, lines 2996–3008](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2996-L3008)). Likewise, `kicad-cli` failure returns an empty component list, which the add helper treats as a no-op rather than a conflict ([`python/commands/schematic_handlers.py`, lines 3020–3033](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3020-L3033) and [lines 3152–3154](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3152-L3154)).

This is materially weaker than issue #187's proposed `ready` / `noop` / `conflict` plan contract. Konnect should make incomplete source extraction a conflict, not a successful partial sync.

### Footprint identity and matching

Existing footprints are matched only by the visible reference string:

```text
existing_refs = {fp.GetReference() ...}
if ref in existing_refs: continue
```

That behavior is in the current helper ([`python/commands/schematic_handlers.py`, lines 3156–3176](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3156-L3176)) and is the root cause of the still-open duplicate-footprint report ([issue #250](https://github.com/mixelpixx/KiCAD-MCP-Server/issues/250)). No stable schematic UUID, sheet-instance path, footprint KIID, or topology disambiguation participates in the match.

For matched footprints, the operation does not update reference, value, FPID, library artwork, schematic linkage, placement, side, rotation, or lock state. It only assigns nets to pads. For newly added footprints it sets reference, value, and FPID, but does not establish an explicit stable schematic-path linkage in this code path ([`python/commands/schematic_handlers.py`, lines 3225–3234](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3225-L3234)).

This strongly supports issue #187's proposed stable-identity-first match with reference only as an unambiguous fallback.

### Adds, updates, and removals

The sibling implementation does the following:

- **Adds footprints:** yes, when a missing reference has a resolvable `Library:Name` footprint.
- **Updates existing footprints:** pad net assignment only.
- **Adds nets:** yes, for names produced by the custom connectivity walker.
- **Updates pad nets:** yes, when `(reference, pad number)` exists in the map.
- **Clears stale pad nets:** no; unmatched pads are reported but otherwise left alone.
- **Renames or removes old nets:** no.
- **Remaps track/via/zone net identity:** no.
- **Removes board-only footprints:** no.

The merged footprint-add PR explicitly put removal out of scope and chose conservative preservation, noting that deletion would need a separate explicit opt-in ([PR #171, “Out of scope”](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/171)). That is direct first-party precedent for issue #187's recommended “preserve and report” behavior.

Because old board nets and copper items are not remapped, preservation is physical rather than semantic: tracks, vias, zones, graphics, and existing footprint placement are untouched, but a schematic net rename can leave routing on the old net while pads move to a newly added one. Konnect should preflight this as an unambiguous remap or conflict instead of assuming that “not editing copper geometry” alone preserves routing.

### New-footprint placement

Every added footprint is placed at board origin ([`python/commands/schematic_handlers.py`, lines 3225–3233](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3225-L3233)). The merged PR describes `(0, 0)` as deterministic and leaves an outside-board grid for future work ([PR #171](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/171)). A later tool description openly says sync “piles every footprint at the origin” before hierarchical placement ([`src/tools/component.ts`, around line 954](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/tools/component.ts#L954)).

This supports issue #187's proposed deterministic strip outside the existing layout bounds. It retains determinism without creating a stack of overlapping footprints.

## Hierarchy and multi-unit behavior

The sibling operation improved from root-sheet-only behavior in merged [PR #120](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/120), but its current algorithm is not a true root hierarchy traversal:

- it performs `project_dir.rglob("*.kicad_sch")`, so every schematic file below the directory is included whether or not it is reachable from the requested root;
- it scans each distinct file once rather than each sheet instance;
- it keys connectivity by flat `(reference, pin)` pairs;
- it propagates raw local, global, and hierarchical label names without a sheet-instance namespace.

The implementation evidence is [`python/commands/schematic_handlers.py`, lines 2748–2809](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2748-L2809). The hierarchy tests cover separate top/subsheet files with distinct references, but not repeated sheet instances or orphan files ([`tests/test_hierarchical_pad_net_map.py`, lines 348–416](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/tests/test_hierarchical_pad_net_map.py#L348-L416)).

The geometric net reconstruction also has a current known correctness gap. Open PR #358 reports that unlabeled wire-only nets disappear and that `PWR_FLAG` may be mistaken for a net name; it proposes synthesizing KiCad-compatible anonymous names. Because that PR is still open, it is evidence about a current-main limitation, not landed behavior ([PR #358](https://github.com/mixelpixx/KiCAD-MCP-Server/pull/358)).

Multi-unit support is better at the lower pin-location layer. `PinLocator` tracks a pin's owning unit and resolves each unit's separately placed transform ([`python/commands/pin_locator.py`, lines 49–124](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/pin_locator.py#L49-L124) and [lines 256–350](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/pin_locator.py#L256-L350)). Dedicated tests verify that unit-two pins use the unit-two position ([`tests/test_pin_locator_multi_unit.py`, lines 125–162](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/tests/test_pin_locator_multi_unit.py#L125-L162)). However, there is no end-to-end sync test proving full multi-unit board connectivity.

For Konnect, these findings favor issue #187's proposed KiCad-exported hierarchy/connectivity oracle. The planner may enrich that model with Konnect metadata, but should not reconstruct electrical truth by walking all files and geometrically propagating labels.

## Exclusion, DNP, and BOM semantics

The sync path extracts only `reference`, `value`, and `footprint` from KiCad XML ([`python/commands/schematic_handlers.py`, lines 3057–3068](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3057-L3068)). It does not explicitly read or propagate schematic `on_board`, `in_bom`, or `dnp` flags, and the sync-specific tests contain no cases for them. The repository supports such flags elsewhere, but not in this synchronization algorithm.

Therefore the sibling code is not reliable precedent for the three distinct semantics requested in #187. Konnect should keep them explicit in its desired component model and tests:

- excluded from board: do not add;
- DNP: retain/add board footprint and set DNP;
- excluded from BOM: retain/add board footprint and set BOM exclusion.

Any behavior that happens incidentally because of what a particular KiCad XML exporter includes or omits should be verified by a KiCad-backed fixture before it becomes the Konnect contract.

## Atomicity, rollback, dry-run, and staleness

The sibling operation is **not atomic in the sense proposed by #187**.

- It mutates one SWIG board object sequentially: add footprints, add nets, set pad nets, then save ([`python/commands/schematic_handlers.py`, lines 2942–2985](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L2942-L2985)).
- There is no KiCad IPC commit, rollback block, transaction object, temporary-board swap, or compensation path.
- There is no dry-run or reviewed plan revision in either public schema.
- There is no comparison of current source/target state to previously reviewed state.
- An exception before save may leave the worker's already-loaded in-memory board partially mutated; the handler catches the error but does not restore the object.

The generic Python dispatcher does have a content-signature conflict guard and rotating backups for ordinary SWIG auto-saves ([`python/kicad_interface.py`, lines 1372–1492](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L1372-L1492)). But sync calls `board.Save(board_path)` inside its handler before the dispatcher invokes that generic auto-save path. Sync is merely listed as a mutating command afterward ([`python/kicad_interface.py`, lines 1131–1143](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L1131-L1143) and [lines 1170–1202](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/kicad_interface.py#L1170-L1202)). Consequently, that generic guard cannot preflight or roll back the sync handler's direct write.

The Node bridge serializes requests and grants sync a ten-minute timeout ([`src/command-timeout.ts`, lines 9–28](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/src/command-timeout.ts#L9-L28)). Serialization prevents two worker commands from running simultaneously, but it is not an atomic design transaction and does not detect edits made by KiCad or another process between review and apply.

This is the clearest reason not to reproduce the sibling architecture in Rust. Konnect already has the more appropriate primitive: compute a pure plan, verify an expected revision, then place all IPC mutations in one `run_commit` so failure drops the commit and the user gets one undo entry.

## KiCad and runtime dependencies

The sibling repository requires KiCad 9+, Node 18+, Python 3.9+, and a Python environment that can import `pcbnew`; it lists `kicad-python`, `sexpdata`, and `kicad-skip` as runtime dependencies ([README, lines 655–683](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/README.md#L655-L683) and [`requirements.txt`, lines 1–11](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/requirements.txt#L1-L11)). The sync operation additionally requires `kicad-cli` for adding missing components, even though connectivity is reconstructed separately.

The project supports `auto`, `ipc`, and `swig` backend preferences generally ([README, lines 1022–1039](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/README.md#L1022-L1039)), but sync itself is not IPC-capable in the command table. This dependency split is non-portable to Konnect and is exactly what the Rust/native-IPC rewrite is intended to eliminate.

## Test coverage and gaps

Current tests establish useful pieces but not the full safety contract:

- Footprint-add tests mock the board, `pcbnew`, library manager, and component extraction. They cover adding, already-present references, power references, missing footprint IDs, unknown libraries, and CLI failure ([`tests/test_sync_schematic_to_board_footprints.py`, lines 46–245](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/tests/test_sync_schematic_to_board_footprints.py#L46-L245)).
- XML extraction tests fake `subprocess.run` and write a fixture XML file rather than invoking real KiCad ([`tests/test_sync_schematic_to_board_footprints.py`, lines 253–328](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/tests/test_sync_schematic_to_board_footprints.py#L253-L328)).
- Hierarchy tests use real small S-expression files for pin definitions but mock `kicad-skip` schematic objects ([`tests/test_hierarchical_pad_net_map.py`, lines 29–169](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/tests/test_hierarchical_pad_net_map.py#L29-L169)).
- Multi-unit pin-location tests exercise `PinLocator`, not the complete synchronization operation.

No current sync-specific test proves:

- dry-run purity;
- stale-plan rejection;
- all-or-nothing rollback or undo;
- preservation of placement, lock, side, or routed copper;
- net rename/remap behavior;
- board-only reporting;
- DNP/BOM/board exclusion semantics;
- repeated sheet instances;
- idempotent `noop` classification;
- equivalence of the final board against a KiCad-exported component/net oracle.

The absence of those tests is not merely theoretical: the footprint-add behavior arrived later in PR #171, reference-only matching remains open in issue #250, and unlabeled connectivity is still addressed only by open PR #358. The iterative repair history supports #187's proposed pure planner plus comprehensive fixtures.

## Comparison with the four requested scope decisions in Konnect #187

### 1. Live IPC only for version one

**Sibling precedent:** no. The sibling sync is specifically a SWIG/file mutation, not an IPC command.

**Recommendation for Konnect:** retain “live IPC only” for version one. The sibling repo itself identifies Konnect as the official-IPC successor. Its file/SWIG path demonstrates the state-divergence, rollback, and dependency problems the rewrite is meant to remove. An offline file adapter should remain a later, separately specified implementation of the same pure plan.

### 2. Source of truth

**Sibling precedent:** hybrid and inconsistent. `kicad-cli` supplies the component list, while a custom geometric parser supplies connectivity.

**Recommendation for Konnect:** retain a complete KiCad-generated netlist/connectivity model as the correctness oracle, enriched only where necessary by Konnect parsing. Current sibling defects around unlabeled nets and file-glob hierarchy traversal are direct evidence against reimplementing electrical truth. If live unsaved schematic state cannot be exported by the chosen KiCad interface, that limitation must be an explicit preflight conflict or save requirement, never a silent fallback to partial parsing.

### 3. Board-only footprint removal

**Sibling precedent:** preserve; deletion is explicitly out of scope in merged PR #171.

**Recommendation for Konnect:** retain “preserve and report.” It protects mechanical and intentionally board-only items and aligns with the maintainer's prior accepted conservative scope. A future removal option should require a separate explicit contract.

### 4. New-footprint staging

**Sibling precedent:** deterministic but poor: all new footprints at `(0, 0)`, followed by a separate placement step.

**Recommendation for Konnect:** retain the deterministic outside-layout strip. The sibling project's own documentation and later placement tooling acknowledge the origin pile. Returning staged coordinates in the reviewed plan also makes apply auditable.

## Design ideas worth carrying forward

These are concepts to reproduce cleanly in Rust, not code to copy:

1. **One workflow-level tool.** The public operation should remain a single schematic-to-board synchronization contract rather than exposing the caller to low-level ordering.
2. **KiCad-exported component discovery.** A KiCad-produced flattened design view is the right starting point for hierarchy and repeated instances.
3. **Conservative board-only behavior.** Never infer deletion from absence in the schematic in version one.
4. **Explicit skip/conflict diagnostics.** The sibling's added/skipped lists are useful, but Konnect should promote incomplete prerequisites to conflicts.
5. **Resolve and cache footprint definitions during planning.** The sibling's per-call prototype cache and library-table freshness key show that footprint resolution cost and staleness matter ([`python/commands/schematic_handlers.py`, lines 3078–3133](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3078-L3133) and [lines 3160–3208](https://github.com/mixelpixx/KiCAD-MCP-Server/blob/91189c59ee492bfa7401abf4532d381e32b977ac/python/commands/schematic_handlers.py#L3160-L3208)). In Konnect, resolution results should be part of the plan revision or recomputed before commit.
6. **Return quantitative results.** Added/updated/preserved/skipped/conflicted counts and precise item identities make the operation inspectable.

## Assumptions that should not be carried into Konnect

1. Reference designator equals stable component identity.
2. Every `.kicad_sch` below a directory belongs to the requested hierarchy.
3. Raw label names are sufficient to represent sheet-instance connectivity.
4. A missing `kicad-cli` result means “nothing to add.”
5. Unresolvable footprints can be skipped while reporting overall success.
6. Existing unmatched pad net assignments should be left silently untouched.
7. Preserving geometry alone preserves routed electrical intent after a net rename.
8. A final `board.Save()` is equivalent to a transaction.
9. Request serialization is equivalent to stale-state protection.
10. `(0, 0)` is an acceptable staging area for all new footprints.

## Recommended approval framing for issue #187

The sibling repository gives the maintainer a familiar precedent without requiring Konnect to inherit the older architecture:

> KiCAD-MCP-Server already treats schematic-to-board synchronization as a required, single public workflow operation and already preserves board-only footprints. Its implementation history also exposes the exact failure modes #187 is designed to avoid: reference-only duplicates, incomplete custom net reconstruction, origin-stacked footprints, successful partial skips, and no transactional dry-run/apply boundary. Konnect should implement the same user capability natively in Rust using its official KiCad IPC commit model, with KiCad-generated hierarchy/connectivity as the oracle, a pure reviewed plan, stale-plan rejection, and one rollback-capable apply.

That framing uses the sibling project as evidence of user need and prior maintainer direction while keeping the Konnect implementation smaller, safer, and consistent with the stated purpose of the Rust rewrite.
