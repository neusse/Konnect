# KiCad 10.0.5 IPC footprint-creation crash research

Research date: 2026-08-16  
Observed KiCad build: Windows x64 `10.0.5.50609`  
Scope: official KiCad documentation, source, libraries, issue tracker, and official `kicad-python` tracker; local Konnect source and reproduced tests

## Incident request

Konnect v0.6.0 can terminate the running KiCad 10.0.5 process while placing an
official library footprint through live IPC. The immediate trigger is a valid
footprint graphic on `Dwgs.User`: Konnect maps that layer to `BL_UNDEFINED`, and
KiCad faults while consuming the invalid scalar layer instead of returning an
API error. This can discard unsaved work in the active KiCad session.

### Minimal reproduction

1. Create an empty KiCad project and open its PCB in KiCad 10.0.5 with the API
   enabled.
2. Load Konnect's `pcb_components` toolset.
3. Call `place_component` against the active board with either exact footprint:

   ```json
   {
     "board": "<active-board>.kicad_pcb",
     "footprint": "Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal",
     "reference": "J1",
     "x": 100,
     "y": 100
   }
   ```

   or `Connector:BJB_Pico_46.110.1001_Receptacle_Horizontal`.
4. KiCad exits during `CreateItems`. Konnect reports an NNG receive timeout;
   Windows records exception `0xc0000005` in `kicommon.dll` at offset `0x87e70`.

The USB-C footprint also reproduces through `update_pcb_from_schematic`; simple
footprints and multiple targeted pad-construction controls succeed.

### Expected

The footprint is created with its `Dwgs.User` graphics intact. If a future layer
cannot be represented, Konnect returns a structured error before sending any
mutation to KiCad. KiCad must not be terminated.

### Actual

Konnect serializes `Dwgs.User` as `BL_UNDEFINED`. KiCad terminates with a native
access violation, the IPC call times out, and unsaved session work is at risk.

### Relationship to #232

#232 is a practical prerequisite or overlapping dependency: it already adds the
missing `Dwgs.User`, `Cmts.User`, `F.Adhes`, and `B.Adhes` mappings. However, it
is a much larger feature PR, is currently conflicting, and does not include the
two exact crash regressions or a fail-closed unknown-layer boundary. This bug
should be resolved either by extracting that mapping into a focused fix first,
or by augmenting and verifying #232 before considering the incident closed.

### Acceptance criteria

- Valid KiCad graphic layers used by the two fixtures never serialize as
  `BL_UNDEFINED`.
- Unknown write-layer names return a structured error before `CreateItems` or
  `UpdateItems`; they never fall through to `BL_UNDEFINED`.
- Both exact official footprints place successfully through live KiCad 10.0.5,
  retain their `Dwgs.User` children, and leave KiCad responsive.
- USB-only `update_pcb_from_schematic` succeeds, followed by the complete
  benchmark synchronization without a native crash.
- Unit coverage pins the valid mappings and rejects unknown write layers; an
  ignored disposable live-KiCad regression covers the two exact fixtures.

## Executive conclusion

The reproducer identifies a specific, coherent primary cause: Konnect does not recognize the valid KiCad footprint layer `Dwgs.User`. While building either of two affected official footprints, it converts every `Dwgs.User` graphic to the protocol value `BL_UNDEFINED`. KiCad 10.0.5 accepts scalar graphic layers without validating them, and both observed Windows faults resolve to `sul::dynamic_bitset<...>::operator[]+0x10`, the container KiCad uses for board-layer sets.

The causal chain is:

1. Both independently crashing official footprints contain lines or text on `Dwgs.User`.
2. Konnect's `layer_from_name()` lacks `Dwgs.User` and falls through to `BlUndefined`.
3. Konnect serializes that value into footprint child `PCB_SHAPE`/`PCB_TEXT` messages.
4. KiCad deserializes those scalar layers with `SetLayer(...)` and no validity check.
5. The process faults in the dynamic-bitset subscript used underneath KiCad layer sets.
6. Control footprints without unsupported user-layer graphics succeed.

This makes the old-file-format warning, footprint count, complex pad construction, and the separate two-editor IPC defect unnecessary to explain this crash. A live test after correcting the mapping is still required to close the loop end to end.

## Exact reproduced fixtures

Each of these official KiCad 10.0.5 library footprints crashes an ordinary Konnect `place_component` operation by itself:

- [`Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal`](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/10.0.5/Connector_USB.pretty/USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal.kicad_mod) contains a `Dwgs.User` line and `PCB Edge` user text.
- [`Connector:BJB_Pico_46.110.1001_Receptacle_Horizontal`](https://gitlab.com/kicad/libraries/kicad-footprints/-/blob/10.0.5/Connector.pretty/BJB_Pico_46.110.1001_Receptacle_Horizontal.kicad_mod) contains multiple `Dwgs.User` lines and user-text items.

The USB-C footprint also crashes `update_pcb_from_schematic`. Controls without unsupported user-layer graphics succeed. This common input property across two otherwise different footprints is stronger evidence than the earlier one-simple-versus-twelve-complex comparison.

The installed faulting module is `kicommon.dll` version `10.0.5.50609`, SHA-256 `B9CFCB5AAB20710112CE1840AFD39EF5C2DA04C5D371C978E4416A926CF4CB4C`. Windows recorded exception `0xc0000005` at module offset `0x87e70` twice. KiCad's official stable symbol server resolves that address to:

```text
sul::dynamic_bitset<unsigned __int64, std::allocator<unsigned __int64>>::operator[]+0x10
```

KiCad's [`BASE_SET`](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/include/base_set.h) derives from `sul::dynamic_bitset<uint64_t>`, and the board-layer [`LSET`](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/include/lset.h) derives from `BASE_SET`.

## Local serialization defect

In `crates/konnect-ipc/src/builders.rs`, `layer_from_name()` recognizes common copper, mask, paste, silkscreen, courtyard, and fabrication layers, but not `Dwgs.User`, `Cmts.User`, `F.Adhes`, or `B.Adhes`. Its catch-all result is `BoardLayer::BlUndefined`.

The graphic builders then assign that result directly to protocol messages:

- `board_shape()` assigns the mapped value to `PCB_SHAPE.layer`;
- `board_text()` assigns it to `PCB_TEXT.layer`;
- the footprint-building path appends those graphic children to the `FootprintInstance` sent through `CreateItems`.

The [KiCad 10.0.5 board API protocol](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/api/proto/board/board_types.proto) defines `BL_UNDEFINED`. On the receiving side, [`PCB_SHAPE::Deserialize`](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/pcbnew/pcb_shape.cpp#L103) and [`PCB_TEXT::Deserialize`](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/pcbnew/pcb_text.cpp#L137) pass the converted scalar layer directly to `SetLayer(...)`; neither validates that it is a usable board layer first.

This is not merely a symbol-based guess: the invalid value is observable in the local construction path, the two minimal failing fixtures share the exact triggering layer, controls do not, and the native fault is in the expected data structure. The remaining uncertainty is whether a corrected mapping alone eliminates every crash in the full benchmark.

## Official KiCad precedent for invalid layers causing native crashes

KiCad [issue #21743](https://gitlab.com/kicad/code/kicad/-/issues/21743) reported an IPC crash while creating and placing a `FootprintInstance` containing a pad with invalid layer data. Fix [`66628a35`](https://gitlab.com/kicad/code/kicad/-/commit/66628a3501e29f140a450c03e6c9fd6c5f1ecf3a) changed `UnpackLayerSet` to reject protocol-layer values that do not map to valid internal board layers. That fix is present in 10.0.5, but it protects packed layer *sets*, not the unvalidated scalar graphic-layer deserializers above.

KiCad [issue #19750](https://gitlab.com/kicad/code/kicad/-/issues/19750) is a non-IPC precedent in which an undefined layer value reached KiCad's dynamic bitset during blind-via placement and crashed. It independently establishes that an invalid layer can fail in the exact container family identified in the reproduced fault.

## Existing Konnect PR overlap

Open Konnect [PR #232](https://github.com/mixelpixx/Konnect/pull/232), `feat(pcb): update placed footprints from libraries`, already adds mappings for `Dwgs.User`, `Cmts.User`, `F.Adhes`, `B.Adhes`, additional user layers, and more inner copper layers. It also adds unit coverage for several of those mappings.

That change would address the immediate mapper defect, but the PR is a much larger, unrelated feature change, is currently reported as conflicting, and does not document this native crash or include the two exact live-placement regressions. Its CI jobs were green at the time of research. The safest integration choices are either:

- extract the layer-mapping change and focused regression tests into a small crash-fix PR; or
- if #232 is intentionally merged first, rebase/resolve it and add crash-specific tests before considering this incident closed.

Avoid silently sending `BL_UNDEFINED` for future unknown write layers. The durable boundary should reject an unmapped layer with a structured error before calling KiCad, rather than relying only on an ever-growing mapping table.

## Separate current KiCad risk: first write with two editors open

Open KiCad [issue #24966](https://gitlab.com/kicad/code/kicad/-/issues/24966) describes a different Windows KiCad 10.0.4 failure: `Board.update_items()` can terminate KiCad when Schematic and PCB Editors are both open and no interactive PCB edit/save has occurred. PCB-only sessions passed 3/3 for that reporter, and a trivial interactive PCB edit plus save prevented later failures.

KiCad 10.0.5 registers `CreateItems` and `UpdateItems` through the same editor-handler framework in [`common/api/api_handler_editor.cpp`](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/common/api/api_handler_editor.cpp). Its `checkForBusy()` dereferences `m_frame` without a null check. Current master commit [`caf1bcc4`](https://gitlab.com/kicad/code/kicad/-/commit/caf1bcc4559bcbede1e4791f024c886a5825153e) adds a null guard for headless API-server work, but does not claim to fix #24966 and is not in 10.0.5 or the current `10.0` stable branch.

This remains worth a separate PCB-only first-write regression. It is not the primary explanation here: #24966 faulted in `_eeschema.dll`, while the reproduced failures fault in `kicommon.dll` at dynamic-bitset access and isolate cleanly to two `Dwgs.User` footprints.

## Older incidents and negative search results

- [#20206](https://gitlab.com/kicad/code/kicad/-/issues/20206) and duplicate [#20490](https://gitlab.com/kicad/code/kicad/-/issues/20490) concerned IPC footprint-update crashes fixed for KiCad 9.0.1; those fixes predate 10.0.5.
- [#21340](https://gitlab.com/kicad/code/kicad/-/issues/21340) concerned duplicate child UUIDs and was fixed for 9.0.7; 10.0.5 regenerates child UUIDs during creation.
- Official core and `kicad-python` trackers produced no matching report that attributes a 10.0.5 `CreateItems` crash to valid `Dwgs.User` graphics specifically, paste-only pads, overlapping/duplicate pads, or NPTH/PTH construction by itself.

The absence of an exact upstream report does not weaken the local mapper evidence; it means this Konnect-to-KiCad invalid-value path may not yet have a dedicated KiCad incident.

## Recommended fix and verification

1. Add a failing unit test proving `layer_from_name("Dwgs.User")` must map to `BlDwgsUser`, with adjacent coverage for `Cmts.User`, `F.Adhes`, and `B.Adhes`.
2. Add a regression that parses/builds each exact official failing footprint and asserts that no graphic child carries `BL_UNDEFINED`.
3. Add the missing valid mappings. Prefer changing the write boundary to return an error for any still-unknown layer instead of serializing `BL_UNDEFINED`.
4. In fresh disposable projects, run `place_component` for each exact footprint, query the board, and verify KiCad remains alive and the footprint plus `Dwgs.User` children exist.
5. Repeat the USB-only `update_pcb_from_schematic`, then the full 12-footprint benchmark.
6. Separately retain a PCB-only cold-session run to screen for KiCad #24966.

Until fixed, avoid Konnect placement/synchronization of footprints whose child graphics use currently unmapped layers. Removing valid library graphics is only a diagnostic workaround; correcting the mapping and rejecting unknown write layers is the appropriate solution.
