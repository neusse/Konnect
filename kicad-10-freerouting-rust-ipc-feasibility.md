# Stock KiCad 10 Freerouting round-trip with Rust and IPC

**Research date:** 2026-08-25  
**Target:** unmodified KiCad 10.0.5, a Rust Konnect client, and the standalone
Freerouting JAR. No Python, SWIG, GUI automation, or direct editing of a board
owned by KiCad.

## Feasibility judgment

**Yes.** A rules-compliant solution can be built against stock KiCad 10.0.5,
but Konnect must implement the interchange adapter itself:

1. read the live board through KiCad 10 IPC;
2. generate a Freerouting-compatible Specctra DSN in Rust;
3. run the standalone Freerouting JAR to produce SES;
4. parse the SES in Rust; and
5. apply tracks, arcs, and vias through one KiCad 10 IPC commit.

KiCad 10.0.5 has enough typed IPC data and mutation operations for that flow.
It does **not** expose native DSN export or SES import over IPC, and
`kicad-cli` never offered those commands. This is therefore a real DSN writer
and SES parser project, not a thin call-through.

The current `konnect-codex` bridge cannot be the implementation: it launches
Python, imports legacy `pcbnew`, and calls SWIG `ExportSpecctraDSN` /
`ImportSpecctraSES`
([companion source](https://github.com/neusse/konnect-codex/blob/d4f51ca3ad28932ee0bd7e441cf7196ef76b81ee/src/lib.rs)).
That violates the no-Python boundary and has no future in KiCad 11, where SWIG
is scheduled for removal
([KiCad add-on guidance](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/)).

## Source baseline

- KiCad 10.0.5 official tag commit:
  `18fb9289ff0efdca53c0352ed81a0973f0a6b58c`.
- Freerouting source inspected:
  `1c85a953732f65b1c5866cdfeb5897c8c55186f0`.
- Upstream Konnect source inspected:
  `8648fe2573377eac78525907cbdd16216986f08e`.
- Local companion source inspected:
  `d4f51ca3ad28932ee0bd7e441cf7196ef76b81ee`.

KiCad describes IPC as a language-agnostic Protocol Buffers API carried over
NNG request/reply IPC. In KiCad 10 it controls a running GUI instance; headless
`kicad-cli api-server` is a KiCad 11 addition. Executable plugins may be
compiled programs, so Rust is a supported client architecture
([official add-on documentation](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/),
[wire protocol](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-kicad-developers/)).

## What stock KiCad 10.0.5 does not provide

There is no `board_jobs.proto` in the KiCad 10.0.5 IPC schema and no Specctra
message in any 10.0.5 protobuf. The PCB API handler registers board, item,
transaction, net, zone, and editor operations, but no DSN exporter or SES
importer
([KiCad 10.0.5 API protobuf tree](https://gitlab.com/kicad/code/kicad/-/tree/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto),
[PCB API handler](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/pcbnew/api/api_handler_pcb.cpp)).

The current KiCad CLI command sources likewise contain no Specctra export or
import command
([official KiCad 10.0.5 CLI source](https://gitlab.com/kicad/code/kicad/-/tree/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/kicad/cli)).
Upstream Konnect issue #253 correctly records that these commands were absent,
not removed in KiCad 10
([issue #253](https://github.com/mixelpixx/Konnect/issues/253)).

The PCB editor still has GUI actions named
`pcbnew.EditorControl.exportSpecctraDSN` and
`pcbnew.EditorControl.importSpecctraSession`, but they open file selectors.
IPC `RunAction` accepts only an action-name string, not a path, and its schema
explicitly warns that action strings are not a stable API
([GUI actions](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/pcbnew/tools/pcb_actions.cpp),
[RunAction contract](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/commands/editor_commands.proto)).
Driving those dialogs would be GUI automation, which issue #253 rejects as a
durable tool contract.

## Why KiCad 11 messages cannot solve stock KiCad 10

KiCad 11 development adds headless operation and typed export-job messages, but
those messages are not server-side capabilities that a client can backport by
copying newer `.proto` files. An IPC request is packed in protobuf `Any`; KiCad
dispatches it by its fully qualified message type. Stock KiCad 10 has no
registered handler for a KiCad 11-only job type, so the request is unhandled.
Even current KiCad 11 `board_jobs.proto` has no Specctra DSN or SES operation
([KiCad 11 development board jobs](https://gitlab.com/kicad/code/kicad/-/blob/c66f160e5e5f33b78eb45f2a1265dcea0a13ea91/api/proto/board/board_jobs.proto),
[KiCad 10 envelope/status codes](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/envelope.proto)).

Some existing messages also evolve additively. For example, KiCad 10's
`BeginCommit` is empty and its `EndCommit` has no document header, while the
KiCad 11 development schema adds document headers. Protobuf may ignore unknown
fields, but ignoring a new field does not add the newer behavior to the old
server. Konnect must compile and send the KiCad 10.0.5 message shapes when
connected to KiCad 10, selected after `GetVersion`; it must not treat a newer
client schema as capability negotiation
([KiCad 10 editor commands](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/commands/editor_commands.proto),
[KiCad 11 development editor commands](https://gitlab.com/kicad/code/kicad/-/blob/c66f160e5e5f33b78eb45f2a1265dcea0a13ea91/api/proto/common/commands/editor_commands.proto)).

## KiCad 10 IPC data available to a Rust DSN writer

Stock 10.0.5 exposes the core routing model:

| DSN concern                   | KiCad 10.0.5 IPC source                                         |
| ----------------------------- | --------------------------------------------------------------- |
| Active-board identity         | `GetOpenDocuments`, `DocumentSpecifier`                         |
| Layer count, names, stackup   | `GetBoardEnabledLayers`, `GetBoardLayerName`, `GetBoardStackup` |
| Nets                          | `GetNets`                                                       |
| Explicit/effective netclasses | `GetNetClasses`, `GetNetClassForNets`                           |
| Footprints and pads           | `GetItems` with `KOT_PCB_FOOTPRINT` and `KOT_PCB_PAD`           |
| Board boundary and obstacles  | `GetItems` with `KOT_PCB_SHAPE` and `KOT_PCB_ZONE`              |
| Existing routing              | `GetItems` with `KOT_PCB_TRACE`, `KOT_PCB_ARC`, `KOT_PCB_VIA`   |
| Exact flashed pad geometry    | `GetPadShapeAsPolygon`, `CheckPadstackPresenceOnLayers`         |
| Stable live snapshot text     | `SaveDocumentToString`                                          |

The command definitions are in the official
[board command protobuf](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/board/board_commands.proto),
[editor command protobuf](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/commands/editor_commands.proto),
and
[project command protobuf](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/commands/project_commands.proto).

The corresponding typed board model includes:

- tracks with start/end, width, layer, net, and lock state;
- arcs with start/mid/end, width, layer, net, and lock state;
- vias with position, layer span, padstack, type, net, and lock state;
- pads with number, net, padstack, and footprint-local position;
- footprint instances with placement, rotation, board side, and child items;
- board graphical shapes;
- zones and rule areas with outlines, layers, and copper settings; and
- nets identified by name (net code is deprecated).

See the official
[board item messages](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/board/board_types.proto)
and
[object-type enum](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/types/enums.proto).
Coordinates and distances are signed 64-bit nanometres
([common types](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/types/base_types.proto)).

### Known read-side gaps

KiCad 10.0.5 does not expose the newer `GetBoardDesignRules` or
`GetCustomDesignRules` commands. It does expose explicit project netclasses and
the effective class for each net, which covers ordinary width, clearance, via,
and differential-pair settings, but not every `.kicad_dru` condition. A pure
IPC bridge cannot claim that all custom-rule semantics were lowered to DSN.

The correct behavior is to export the effective per-net routing values that IPC
does provide, disclose that arbitrary custom rules are not representable, and
make post-import KiCad DRC an acceptance gate. If the workflow requires proof
that no unobserved custom rule matters before routing, stock KiCad 10 IPC alone
cannot provide that proof; the tool must refuse rather than synthesize an
answer.

`GetPadShapeAsPolygon` also documents that curves are approximated as segments.
That is acceptable only with a declared tolerance and parity tests against
KiCad's native DSN output.

## Rust DSN exporter design

The exporter should be a deterministic adapter over one immutable IPC snapshot,
not a series of loosely related live reads.

### 1. Acquire and bind the snapshot

1. Require exactly one responsive PCB editor.
2. Resolve the requested path through `GetOpenDocuments` and Konnect's existing
   `ensure_board_is_active` guard.
3. Call `SaveDocumentToString` and hash the returned content as the snapshot
   revision.
4. Query all required typed data against that `DocumentSpecifier`.
5. Before import, repeat the snapshot hash and refuse if the live board changed.

This preserves Konnect's single-owner rule and prevents exporting one board but
importing into a later revision.

### 2. Build a normalized Rust routing model

Normalize KiCad nanometres to one documented DSN resolution. Preserve a reverse
manifest beside the temporary DSN containing:

- source board path, token, snapshot hash, and KiCad version;
- DSN layer index/name to KiCad layer enum;
- DSN net ID to KiCad net name;
- DSN component/image/pin names to footprint and pad KIIDs;
- DSN via-padstack names to exact KiCad via type, diameter, drill, and layer
  span; and
- the coordinate origin, scale, rotation, and back-side transform.

The manifest is essential for importing SES without guessing.

### 3. Emit the DSN sections

The Rust writer needs the subset Freerouting and KiCad round-trip:

- `parser`, `resolution`, and `unit`;
- `structure`: copper layers, boundary, keepouts/obstacles, default rule, and
  permitted via padstacks;
- `placement`: component location, side, and rotation;
- `library`: footprint images, outlines, and pin/pad shapes;
- `network`: nets, pins, classes, widths, clearances, and via rules; and
- `wiring`: existing tracks/arcs/vias with locked routing protected.

Freerouting's official CLI consumes `.dsn` with `-de` and produces `.ses` with
`-do`; its current source owns dedicated `DsnReader`, `DsnWriter`, `SesReader`,
and `SesWriter` implementations
([CLI documentation](https://github.com/freerouting/freerouting/blob/1c85a953732f65b1c5866cdfeb5897c8c55186f0/docs/command_line_arguments.md),
[Specctra I/O package](https://github.com/freerouting/freerouting/tree/1c85a953732f65b1c5866cdfeb5897c8c55186f0/src/main/java/app/freerouting/io/specctra)).

The writer should produce stable ordering and canonical quoting so golden files
are reviewable. It must fail closed on an unsupported boundary, padstack,
keepout, rule, or coordinate transform; dropping the feature is not allowed.

## Rust SES parser and IPC import design

The SES parser needs only the session subset that Freerouting emits, not every
historical Specctra construct. Its ground truth should be Freerouting's
`SesWriter` and KiCad's native `specctra_import.cpp`, with fixtures from both
projects.

### Parse into an import plan

Parse placement changes, `network_out`, route library/padstacks, wires
(`path` and `qarc`), and vias. Resolve every name through the export manifest.
Reject the complete session if it contains:

- an unknown net, layer, component, pin, or via padstack;
- a coordinate outside the expected transform/range;
- a width, drill, diameter, or layer span that cannot be represented by the
  KiCad 10 protobuf;
- a placement change when placement import was not explicitly enabled; or
- references inconsistent with the current snapshot.

KiCad's native importer is behavioral ground truth: it preserves locked/fixed
routing, replaces unlocked routing, imports path and QARC geometry plus vias,
can update placement, and keeps the board's own zones rather than importing
session pour polygons
([KiCad 10.0.5 native SES importer](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/pcbnew/specctra_import_export/specctra_import.cpp)).

### Apply one undoable transaction

1. Revalidate the board token, path, and snapshot hash.
2. `BeginCommit` using the KiCad 10 empty request shape.
3. Query current traces, arcs, vias, footprints, and locks again.
4. `DeleteItems` only for unlocked routing selected for replacement.
5. `UpdateItems` only for allowed placement changes.
6. `CreateItems` containing typed `Track`, `Arc`, and `Via` protobufs.
7. Check every per-item result. `IRS_OK` is only the request-level status and
   can accompany individual failures.
8. On any mismatch or item failure, call `EndCommit(CMA_DROP)`.
9. Otherwise call `EndCommit(CMA_COMMIT, "Import Freerouting route")`, producing
   one KiCad undo entry.
10. Refill zones and handle `AS_BUSY` with bounded polling.
11. Use `SaveCopyOfDocument` to write a non-overwriting
    `<stem>.freerouted.kicad_pcb` acceptance candidate while leaving the source
    board file untouched.
12. Run direct KiCad DRC on that copy and report route/via inventory, remaining
    unrouted connections, shorts, width mismatches, and violations. A failed
    acceptance remains one recoverable Ctrl-Z operation in the live editor.

The transaction, per-item status, save-copy, and zone commands are defined in
the KiCad 10.0.5
[editor protobuf](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/common/commands/editor_commands.proto)
and
[board protobuf](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/api/proto/board/board_commands.proto).

## Fit with Konnect's existing Rust code

Upstream Konnect already has most of the write-side foundation:

- active-board identity checks;
- `GetNets` and generic `GetItems`;
- typed track and via builders;
- `CreateItems`, `UpdateItems`, and `DeleteItems` with per-item checks;
- commit/push/drop helpers;
- zone refill and save; and
- board layer queries.

Those methods are in
[`konnect-ipc/src/client.rs`](https://github.com/mixelpixx/Konnect/blob/8648fe2573377eac78525907cbdd16216986f08e/crates/konnect-ipc/src/client.rs)
and
[`builders.rs`](https://github.com/mixelpixx/Konnect/blob/8648fe2573377eac78525907cbdd16216986f08e/crates/konnect-ipc/src/builders.rs).

An existing Rust dependency may shorten the format work. The MIT-licensed
`topola_specctra` 0.1.0 crate describes itself as a DSN/SES parser and
serializer and exposes Specctra structures plus reader/writer machinery
([crate registry entry](https://crates.io/crates/topola_specctra/0.1.0),
[published source](https://docs.rs/crate/topola_specctra/0.1.0/source/)). It is a
candidate component, not yet evidence of Freerouting round-trip compatibility.
Before adopting or vendoring it, run its parser against Freerouting's complete
SES fixture corpus and generated sessions, including optional and unfamiliar
scopes, then run its writer against the KiCad/Freerouting DSN corpus. Konnect
should retain its own strict lowering and manifest resolution layer even if it
reuses the crate's tokenizer or syntax model. Any valid Freerouting output the
crate cannot represent must cause an explicit unsupported-session failure, not
partial import.

Required IPC additions are wrappers for the already-vendored KiCad 10 messages:

- `GetBoardStackup`;
- `GetNetClasses` and batched `GetNetClassForNets`;
- `GetPadShapeAsPolygon`;
- `CheckPadstackPresenceOnLayers`;
- `SaveDocumentToString`; and
- `SaveCopyOfDocument` if not already exposed at the Konnect client level.

Required new Rust modules are logically:

- `freerouting/model.rs` — immutable normalized board and import-plan types;
- `freerouting/dsn.rs` — canonical writer plus validation;
- `freerouting/ses.rs` — parser plus manifest resolution;
- `freerouting/runner.rs` — JAR discovery/execution, timeouts, and artifact
  retention; and
- `tools/freerouting.rs` — status/export/route/import handlers and acceptance
  reporting.

Upstream Roadmap item 3 requires the standalone JAR, separate reporting of
“engine found” and “bridge available,” cross-platform PCM JAR discovery, board
identity validation, and atomic import
([upstream Roadmap](https://github.com/mixelpixx/Konnect/blob/8648fe2573377eac78525907cbdd16216986f08e/ROADMAP.md)).
Issue #253 additionally requires correct netclass widths, changed-route and
remaining-unrouted evidence, and rejects GUI automation
([issue #253](https://github.com/mixelpixx/Konnect/issues/253)).
This design satisfies those constraints.

The companion policy also requires Freerouting-first routing, single live-board
ownership, a non-overwriting result, import inventory, and direct DRC acceptance
([companion policy](https://github.com/neusse/konnect-codex/blob/d4f51ca3ad28932ee0bd7e441cf7196ef76b81ee/policy/enhancements.json)).
Once the Rust IPC bridge is verified, the Python `offline-freerouting-bridge`
enhancement should be retired rather than retained as a fallback.

## Verification required before claiming support

Use KiCad- and Freerouting-owned fixtures plus boards saved by stock KiCad
10.0.5. For every supported case, compare the Rust DSN with KiCad's native DSN
semantically, not byte-for-byte:

- copper layers and names;
- board boundary, cutouts, keepouts, and obstacles;
- footprint placement and transformed pad centers;
- per-layer pad polygons and drills;
- nets and pin membership;
- effective track widths, clearances, and via choices;
- preserved locked routing; and
- existing wiring.

Then route and import, checking:

- all Freerouting wires/vias were either imported or explicitly rejected;
- no source item outside the import plan changed;
- one undo reverses the whole import;
- source board bytes remain untouched until explicit acceptance;
- read-back track/via counts and geometry match the plan;
- remaining unrouted count is reported; and
- KiCad DRC supplies the final acceptance evidence.

Test at minimum two-layer, four-layer, back-side footprints, rotated/custom
pads, slots, blind/buried vias, board cutouts, rule areas, copper zones, Unicode
net names, named/effective netclasses, pre-routed locked nets, and Freerouting
failure/timeout output. Unsupported cases must fail before mutation.

For the first deliverable, a deliberately narrower fail-closed profile is
reasonable: two-layer boards with ordinary plated through pads/vias, simple
closed boundaries, no placement changes, no custom-rule claims, and no existing
unlocked routing. Reject pre-routed boards and unsupported geometry before
writing DSN. Expanding that profile should be driven by fixture parity tests,
not by silently approximating features.

## Reusing KiCad development code

KiCad 11 development sources are useful immediately as a behavioral reference,
especially the protobuf schema, native DSN writer, SES reader, coordinate
transforms, and geometry handling. They cannot add server capabilities to a
stock KiCad 10 process: the shipped KiCad 10 dispatcher still has to recognize
and implement every request.

A clean Rust implementation of the documented protocol and file formats is the
lowest-risk approach. If implementation code is directly copied or closely
translated from KiCad, preserve its notices and review the license header of
each source file. KiCad's repository is primarily GPL-3.0 and Konnect is
AGPL-3.0, so this is not a permissive-code reuse situation even though both are
copyleft projects
([KiCad license](https://gitlab.com/kicad/code/kicad/-/blob/18fb9289ff0efdca53c0352ed81a0973f0a6b58c/LICENSE),
[Konnect license](https://github.com/mixelpixx/Konnect/blob/8648fe2573377eac78525907cbdd16216986f08e/LICENSE)).

## Bottom line

The stock KiCad 10.0.5 gap is solvable today with **Rust on both sides of the
KiCad boundary**: typed IPC board reads, a Rust DSN writer, Freerouting's normal
JAR, a Rust SES parser, and one typed IPC transaction for import. No Python and
no modified KiCad build are required.

The limiting work is faithful format conversion and verification, especially
custom rules and complex geometry. KiCad 11 protobuf/job definitions do not
remove that work for a stock KiCad 10 server and must not be used as if they
were downlevel feature flags.

This conclusion is specifically about the data bridge. Freerouting still runs
as its standalone Java process. KiCad 10 IPC also has no native DRC request, so
a fully automated final KiCad DRC must use the existing `kicad-cli` subprocess
(as Konnect already does) or be performed interactively in the editor. If
project policy forbids `kicad-cli` as well as Python, the Rust/IPC bridge can
still export and atomically import routing, but it cannot automatically complete
the native KiCad DRC acceptance gate on stock KiCad 10.
