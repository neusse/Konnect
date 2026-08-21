# KiCad 10 compatibility, deprecation, and removal audit

Published as [Konnect discussion #224](https://github.com/mixelpixx/Konnect/discussions/224).

Research date: 2026-08-15  
Konnect revision examined: `c74ebb01ee2376c53ce29cefe51a870d69d88130`  
KiCad baseline: 10.0.5 (released 2026-07-22). KiCad 10.0.0 was released 2026-03-20.

## Executive conclusion

There is no single official “everything removed in KiCad 10” page. The defensible list comes from comparing the official KiCad 9 and 10 CLI manuals and command-registration source, then separately checking the IPC API, legacy `pcbnew` Python bindings, plugin manifests, and file-format writers.

For Konnect, the confirmed KiCad 10 CLI removals are low impact: the singular `pcb export gerber` command and the deprecated `--plot-invisible-text` option disappeared, and Konnect uses neither. The repository's claims that KiCad 10 removed `sch annotate`, `pcb sync`, and Specctra DSN/SES CLI commands should be corrected: none appears in the official KiCad 8, 9, or 10 CLI command set. They are absent CLI capabilities, not proven KiCad 10 removals.

Freerouting itself **does work with KiCad 10** through the KiCad Freerouting ActionPlugin. A live Windows test with plugin version 2.3.0 successfully exported DSN through `pcbnew.ExportSpecctraDSN`, ran Freerouting, imported the resulting session through `pcbnew.ImportSpecctraSES`, and refreshed the PCB editor. The defect is narrower: Konnect's MCP `autoroute` handler is disabled even though its README, registry, and tool description advertise it. This must not be reported as a missing KiCad 10 or Freerouting capability.

The important forward-compatibility issue is KiCad 11: KiCad officially says the legacy SWIG `pcbnew` Python bindings are removed there. That breaks Konnect's `plugin/__init__.py` ActionPlugin launcher/settings UI. Konnect's separate executable `plugin.json` IPC plugin follows the replacement architecture and should remain viable, but it does not by itself reproduce all of the legacy dialog and process-lifecycle behavior.

## Discussion-ready findings

| Surface | KiCad status | Konnect impact | Recommended disposition |
|---|---|---|---|
| CLI `pcb export gerber` (singular) | Deprecated in KiCad 9 with an explicit “will be removed in KiCad 10” notice; absent from KiCad 10 command registration. Replacement: `pcb export gerbers`. | None found: `export_gerber` already calls plural `gerbers`. | Record as **confirmed removed and already migrated**. |
| CLI `--plot-invisible-text` | Deprecated/no-op in 9.0.1 and absent from the KiCad 10 exporter interface. | None found. | Record as **confirmed removed; unaffected**. |
| CLI `pcb export hpgl` and `sch export hpgl` | Still registered in KiCad 10 only as compatibility stubs; they return an error and are documented for future removal. HPGL-only `--pen-size` and `--origin` are also deprecated/no-op. | Konnect exposes neither HPGL command. | Record as **present but nonfunctional; future removal; unaffected**. |
| CLI `sch export bom --include-excluded-from-bom` | Deprecated in 10.0 and has no effect. | Konnect uses the supported exclusion/DNP controls, not this flag. | **Unaffected**. |
| CLI PCB SVG output mode | The implicit single-file default is deprecated; KiCad says a future default will behave like `--mode-multi`. | `export_svg_pcb` passes no mode and treats `output` as one file. This is a real future behavior risk. | Pass the intended mode explicitly and test both output contracts. |
| CLI PCB DXF output mode | The implicit default is deprecated in the same way. | Konnect explicitly passes `--mode-multi`. | **Already insulated**. |
| CLI PCB PDF/SVG `--layers` | KiCad 10 defines one `--layers` argument containing a comma-separated list. | Konnect emits repeated `--layers <layer>` arguments for PDF and SVG. Parser behavior was not live-tested here, so this is a contract mismatch, not a confirmed failure. DXF correctly joins layers. | Change PDF/SVG to one comma-separated value or add a KiCad 10 live test first. |
| CLI `sch annotate`, `pcb sync`, Specctra DSN export/SES import | Not listed or registered in the official KiCad 8, 9, or 10 CLI. KiCad 10's in-editor Python API and Freerouting ActionPlugin successfully perform the Specctra exchange. | `DEV.md`, the `autoroute` handler, and a manufacturing diagnostic call the CLI operations “removed in v10.” Konnect's MCP `autoroute` is advertised but always errors; the independently installed KiCad plugin works. | Reword as **not available through `kicad-cli` (not proven removed)**. Implement a Konnect bridge to the working plugin/API path or label `autoroute` unavailable; do not describe Freerouting itself as unavailable. |
| Legacy `pcbnew` SWIG Python API / `ActionPlugin` | Deprecated starting in KiCad 9; supported in 9/10; officially removed in KiCad 11. | `plugin/__init__.py` imports `pcbnew`, subclasses `pcbnew.ActionPlugin`, and implements the settings/start-stop UI. It will not load in KiCad 11. | Treat as the highest-confidence scheduled break. Move remaining UI/lifecycle behavior to the executable IPC plugin or another supported UI. |
| Executable `plugin.json` IPC action | This is the supported IPC plugin model: the manifest starts an external executable which connects through the IPC API. | `plugin/plugin.json` already declares `bin/konnect.exe`. It is architecturally compatible with the replacement model. | Preserve and test on KiCad 11; do not claim it automatically replaces the legacy settings dialog. |
| IPC `RunAction` / UI action strings | KiCad's own schema explicitly says `TOOL_ACTION` names are **not an API**: names may change or disappear during refactoring. | Konnect implements a generic `run_action` client method, although no current MCP handler was found calling it. | Keep it out of stable capability claims. If exposed later, version-map and runtime-probe every action string. |
| IPC `TextAttributes.visible` | Deprecated since API 9.0.1 because non-field text is always visible. | Konnect still sets it in `konnect-ipc/src/builders.rs`. | Stop relying on it; safe cleanup/migration debt. |
| IPC `NetCode` / `Net.code` | Deprecated: official schema says net codes are no longer used and clients should use the net name. The fields remain in the KiCad 10.0.5 schema and current development schema, so no KiCad 11 removal is confirmed. | Konnect constructs and resolves codes in builders/client and uses them throughout PCB sync. | Migrate to name-based identity where the API permits; track as **deprecated, removal date unknown**, not “removed in 11.” |
| `.kicad_pcb` S-expression nets | KiCad 10's writer serializes named nets inline on pads, tracks, and zones rather than relying on the legacy top-level ordinal net table. | Konnect has KiCad-10-aware named-net parsing/routing code; `add_net` intentionally cannot add an empty top-level table entry to a KiCad 10 board. | Consider the known format change largely adapted, but retain round-trip tests because direct S-expression editing is outside the stable IPC contract. |

## Evidence and source notes

### CLI commands and options

The [KiCad 9 CLI manual](https://docs.kicad.org/9.0/en/cli/cli.html) marks singular `pcb export gerber` for removal in 10 and marks `--plot-invisible-text` deprecated/no-op. The [KiCad 10 CLI manual](https://docs.kicad.org/10.0/en/cli/cli.html) documents the surviving command surface, the nonfunctional HPGL stubs, and the deprecated BOM flag. The [KiCad 10 CLI registration source](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/kicad_cli.cpp) registers plural `gerbers` but not singular `gerber`.

The absence finding for annotation, PCB synchronization, and Specctra exchange is based on all three official command inventories: [KiCad 8](https://docs.kicad.org/8.0/en/cli/cli.html), [KiCad 9](https://docs.kicad.org/9.0/en/cli/cli.html), and [KiCad 10](https://docs.kicad.org/10.0/en/cli/cli.html), plus the [KiCad 9](https://gitlab.com/kicad/code/kicad/-/blob/9.0/kicad/kicad_cli.cpp) and [KiCad 10](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/kicad_cli.cpp) registration source. This establishes “not in the documented CLI since at least KiCad 8,” not that no older release ever had a similarly named command.

These CLI absences must not be confused with GUI capabilities. KiCad's PCB editor retains the Specctra implementation in the [KiCad 10 `specctra_import_export` source](https://gitlab.com/kicad/code/kicad/-/tree/10.0/pcbnew/specctra_import_export); PCB update from schematic is likewise an editor workflow. The issue is lack of a `kicad-cli` entry point for Konnect's current headless workflow, not lack of routing support in KiCad 10.

That distinction was verified locally on 2026-08-15. The KiCad 10 PCM installation at `Documents/KiCad/10.0/3rdparty/plugins/app_freerouting_kicad-plugin` contains Freerouting 2.3.0. Its log records two successful DSN-mode cycles against `PIC16F88_HDLG2416_Clock.kicad_pcb`: DSN export succeeded, Freerouting completed, SES import succeeded, and the KiCad UI refreshed. The project directory also contains multiple DSN/SES routing artifacts from the earlier board workflow. This is direct evidence that the installed ActionPlugin is a functioning fallback and a candidate integration path.

The SVG and DXF mode warnings are explicit in the KiCad 10 [SVG exporter source](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/cli/command_pcb_export_svg.cpp) and [DXF exporter source](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/cli/command_pcb_export_dxf.cpp). The common PCB exporter defines `--layers` as a single comma-separated list in [`command_pcb_export_base.cpp`](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/cli/command_pcb_export_base.cpp). The HPGL error behavior is implemented in the KiCad 10 [PCB HPGL](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/cli/command_pcb_export_hpgl.cpp) and [schematic plot](https://gitlab.com/kicad/code/kicad/-/blob/10.0/kicad/cli/command_sch_export_plot.cpp) sources.

### Python, plugins, and IPC

KiCad's [API and bindings overview](https://dev-docs.kicad.org/en/apis-and-binding/) records the SWIG deprecation, and the official [`kicad-python` project](https://gitlab.com/kicad/code/kicad-python) states the concrete compatibility boundary: legacy SWIG is present in KiCad 9 and 10 and removed in KiCad 11.

KiCad's [add-on developer documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/) describes executable `plugin.json` actions and also records an important architecture constraint: in KiCad 9 and 10 the IPC API is GUI-only and does not expose plotting/export, so invoking `kicad-cli` for those jobs is the intended fallback rather than a deprecated design.

The official [IPC evolution rules](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-kicad-developers/) say deprecated protobuf fields are retained for at least the current major version and may be removed at a later major release, but not a bug-fix release. The exact deprecations are in the KiCad 10.0.5 [`TextAttributes` schema](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/api/proto/common/types/base_types.proto) and [`Net` schema](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/api/proto/board/board_types.proto). `NetCode` remains present in the [current development schema](https://gitlab.com/kicad/code/kicad/-/blob/master/api/proto/board/board_types.proto), so a specific removal release cannot yet be claimed.

Typed protobuf stability does not extend to editor action names. The official [`RunAction` schema comment](https://gitlab.com/kicad/code/kicad/-/blob/10.0.5/api/proto/common/commands/editor_commands.proto#L90) explicitly warns that these names are unstable and intended for low-level prototyping.

### File format

The [official PCB file-format documentation](https://dev-docs.kicad.org/en/file-formats/sexpr-pcb/) explains the date-versioned header and cautions third-party writers about format ownership. For the KiCad 10 net representation, the authoritative primary evidence is the [KiCad 10 PCB S-expression writer](https://gitlab.com/kicad/code/kicad/-/blob/10.0/pcbnew/pcb_io/kicad_sexpr/pcb_io_kicad_sexpr.cpp), which writes named nets on pads, tracks, and zones.

## Known gaps and proposed watch list

- KiCad 10 and its Freerouting plugin were exercised live, but the repeated-`--layers` behavior and complete Konnect CLI export suite were not. A Windows KiCad 10.0.5 smoke test should still cover every CLI wrapper Konnect registers.
- Official manuals document public CLI behavior but do not provide a historical ledger of every internal or UI action. “Absent” is therefore intentionally separate from “removed.”
- No official source found promises that deprecated IPC `NetCode` fields will be removed in KiCad 11. Watch each major-release schema diff rather than assigning an unsupported deadline.
- Direct `.kicad_sch`/`.kicad_pcb` editing has no protobuf-style compatibility guarantee. Diff the official writers and run open/save/DRC/ERC round trips for every KiCad major release.
- KiCad 11 IPC adds capabilities beyond the KiCad 9/10 GUI-only API, but that is an addition, not a KiCad 10 removal; it should be evaluated separately when Konnect declares KiCad 11 support.

Official release references: [KiCad 10.0.0, 2026-03-20](https://www.kicad.org/blog/2026/03/Version-10.0.0-Released/) and [KiCad 10.0.5, 2026-07-22](https://www.kicad.org/blog/2026/07/KiCad-10.0.5-Release/).
