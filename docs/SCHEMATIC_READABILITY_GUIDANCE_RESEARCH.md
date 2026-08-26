# Schematic Readability Guidance Research

**Status:** Research complete; proposed Konnect guidance has not yet been implemented  
**Purpose:** Establish source-backed rules for producing schematics that are both electrically correct and unusually easy to understand  
**Audience:** Future Konnect schematic skills, schematic-builder agents, reviewers, and contributors

## Executive conclusion

An electrically valid schematic and a readable schematic are different deliverables.
KiCad's ERC can detect many connectivity and pin-type problems, but it cannot decide
whether a human can quickly understand the circuit. The future Konnect workflow should
therefore use two independent completion gates:

1. **Electrical gate:** connectivity, pin types, power driving, annotations, footprints,
   no-connect intent, and ERC are correct.
2. **Communication gate:** the rendered drawing exposes functional structure, signal and
   power flow, interfaces, support circuitry, repeated channels, and design intent without
   requiring a reviewer to reconstruct the netlist mentally.

The strongest practical policy is to plan the schematic as a functional document before
placing symbols, build one block at a time, choose connection notation by scope, and perform
a rendered visual review separately from ERC. A schematic that passes ERC but looks like a
component dump is incomplete.

## Source hierarchy and limits

This report uses primary sources only:

- The [KiCad Schematic Editor manual](https://docs.kicad.org/master/en/eeschema/eeschema.html)
  defines KiCad's actual connection, hierarchy, label, bus, power-symbol, grid, and ERC
  behavior.
- The [KiCad Library Convention](https://klc.kicad.org/) defines official-library symbol
  conventions intended to produce cleaner routing and more understandable drawings.
- [IEC 61082-1](https://webstore.iec.ch/en/publication/4469) is the horizontal international
  standard for preparing electrotechnical documents. The IEC describes its rules as focused
  on presenting information so it is correctly understood, independent of the medium; see
  the [IEC TC 3 overview](https://tc3.iec.ch/tc-activity/current_document_kinds/).
- [IEEE/ANSI 315](https://standards.ieee.org/ieee/315/515/) defines standardized graphic
  symbols and modular-grid connection points for electrical and electronic diagrams.
- [IPC-2612](https://www.ipc.org/TOC/IPC-2612.pdf) covers electronic diagramming
  documentation, including legibility, off-page references, bypass capacitors, connecting
  lines, junctions, power and ground, design details, and test points. IPC currently lists
  the 2010 issue as no longer maintained while showing an IPC-2612A revision project in
  development; see IPC's [revision table](https://www.ipc.org/ipc-document-revision-table)
  and [standardization status](https://www.ipc.org/Status).
- First-party component design checklists, such as TI's
  [TUSB4020BI schematic checklist](https://www.ti.com/lit/an/slla408/slla408.pdf) and
  [level-translator schematic checklist](https://www.ti.com/lit/an/spradm1/spradm1.pdf),
  demonstrate that a valid schematic review must include device-specific support circuitry,
  decoupling, power sequencing, defined control states, and unused-pin treatment. Microchip
  applies the same checklist model in its official
  [schematic checklist](https://onlinedocs.microchip.com/oxy/GUID-F9D3C532-E5D3-4B0B-A493-339C2C2521E2-en-US-1/GUID-2A14ABC0-2AB3-4120-873A-E198B8A56337.html).

The public standards pages establish scope and authority but do not expose every detailed
clause. Consequently, this report labels the concrete layout rules below as **Konnect house
rules** where they are a reasoned synthesis rather than a quoted standards requirement.

## 1. Electrical correctness is not readability

| Concern | Electrical correctness asks | Readability asks |
|---|---|---|
| Connectivity | Are the intended pins on the same net? | Can a reader see why those pins belong together? |
| Labels | Do equal names create the intended net? | Does the label scope expose or hide the circuit's structure? |
| Power | Are rails driven and named correctly? | Can the power path, conversion stages, and domains be followed? |
| Components | Are symbols, values, footprints, and pin numbers valid? | Are components visually associated with the function they serve? |
| Hierarchy | Do sheet pins and hierarchical labels match? | Does each sheet have a clear purpose and an understandable interface? |
| Repeated channels | Are all instances connected correctly? | Can a reviewer compare and trace channels without ambiguity? |
| Completion | Does ERC pass? | Does a rendered page communicate the design at normal viewing scale? |

KiCad explicitly describes ERC as a checker for incorrect and missing connections. Its ERC
rules include unconnected pins, undriven inputs and power inputs, conflicting outputs,
unattached labels, unmatched hierarchical pins, conflicting net names, and off-grid
connections. Those checks are necessary, but they do not score page organization,
functional flow, density, or visual ambiguity. The future Konnect agent must never use an
ERC pass as the sole proof of schematic quality.

## 2. Plan the functional architecture before placement

### 2.1 Required pre-placement plan

Before creating symbols, the agent should write a short internal plan containing:

- external inputs and outputs;
- power sources, protection, conversion, and named rails;
- processing or control blocks;
- sensors, interfaces, drivers, loads, and connectors;
- repeated channels;
- configuration, programming, and test functions;
- proposed sheet boundaries and the interface of every sheet.

This follows IPC-2612's stated purpose: a schematic must carry enough information for
inspection, hardware realization, software development, and reuse, including relevant
grounding, power distribution, test points, and I/O locations. It also follows IEC 61082's
document-centered goal that the information be presented for correct human understanding.

### 2.2 One visible narrative per sheet

**Konnect house rule:** Each sheet should have one dominant purpose expressible as a short
title, such as `POWER ENTRY AND 5 V REGULATOR`, `MCU AND PROGRAMMING`, `CAN INTERFACE`, or
`DISPLAY DRIVER CHANNELS`. A sheet may contain several closely related sub-blocks, but it
should not be a storage page for unrelated components.

Arrange major blocks in the order a reviewer naturally follows the design:

- ordinary signal or energy flow primarily left to right;
- supply rails and bias relationships primarily top to bottom;
- inputs and source connectors toward the left/top edges;
- outputs, loads, and destination connectors toward the right edge;
- control and feedback located near the block they control, not in an unrelated page corner.

This convention is consistent with KiCad's official symbol guidance: input/control pins
belong on the left, outputs on the right, positive power at the top, and negative power or
ground at the bottom. Power-conversion symbols are the stated exception: power input on the
left and power output on the right. See
[KLC S4.2](https://klc.kicad.org/symbol/s4/s4.2/).

Do not rotate every part into the same orientation mechanically. Orient the symbol so its
logical function reinforces the sheet's flow. A resistor may be horizontal in a series signal
path and vertical in a pull-up or pull-down branch. A connector may face inward from a page
edge. Consistency serves comprehension, not uniformity for its own sake.

### 2.3 Whitespace is structural

Use whitespace to separate functional blocks before adding graphical boxes. A reviewer
should be able to identify the major regions from spacing, headings, and flow alone.
Optional thin graphic rectangles or separators may reinforce the grouping, but KiCad
graphic lines are not wires and carry no electrical meaning. Borders must not cross wires,
labels, symbols, or text, and they must not imply an electrical connection.

### 2.4 When to split sheets

Create a hierarchical sheet when one or more of these conditions applies:

- a functional block has a clear, limited interface and can be named independently;
- long or crossing connections are needed primarily because unrelated functions share a
  page;
- the page cannot be understood or printed at a normal viewing scale;
- the same functional circuit is instantiated more than once;
- a block is likely to be reviewed, reused, simulated, or replaced independently;
- power, analog, high-speed, safety, or isolation boundaries deserve explicit interfaces.

Keep a design on one sheet when splitting it would hide relationships that are clearer as
short direct wires. Sheet count is not a quality metric: the test is whether hierarchy makes
interfaces and function clearer.

KiCad states that carefully drawn hierarchy improves legibility and reduces repetition.
Hierarchical labels and sheet pins form an explicit parent/child interface, and KiCad can
reuse one child sheet multiple times. The official
[hierarchical schematic documentation](https://docs.kicad.org/master/en/eeschema/eeschema.html#hierarchical-schematics)
and the official [video and multichannel demos](https://gitlab.com/kicad/code/kicad/-/tree/master/demos)
should be used as reference cases.

### 2.5 Root-sheet policy

For a multi-sheet design, the root sheet should behave like a block diagram:

- show every major subsheet;
- arrange sheet symbols in system-flow order;
- expose meaningful interfaces as sheet pins;
- show system-wide rails and external connectors when doing so clarifies the architecture;
- avoid placing detailed support components on the root sheet unless they genuinely belong
  to the system-level interface.

The top sheet is not merely navigation. It is the design's fastest architectural review.

## 3. Wires, labels, and the “flag tag” decision

The user's “flag tags” are normally **net labels**. They must not be confused with KiCad's
`PWR_FLAG`, which is an ERC declaration that a power net is driven when the source does not
have a power-output pin.

KiCad provides two primary connection mechanisms: wires make visible direct connections;
labels connect nets by equal name. Label scope matters:

- a **local label** connects only within its sheet;
- a **global label** connects anywhere in the schematic;
- a **hierarchical label** connects a child sheet to a matching parent sheet pin;
- a **power symbol** names a global power net;
- a **PWR_FLAG** tells ERC that a power net is driven; it does not supply power and should
  not be used as ordinary net-label decoration.

These behaviors are defined in KiCad's
[electrical-connections and labels documentation](https://docs.kicad.org/master/en/eeschema/eeschema.html#electrical-connections).

### 3.1 Decision table

| Situation | Preferred notation | Reason |
|---|---|---|
| Two nearby pins within one functional block | Direct wire | Makes the relationship immediately visible |
| Series chain, divider, filter, bias network, feedback loop, or protection path | Direct wires | Topology is the design information; labels would conceal it |
| Short branch to a nearby pull-up, pull-down, LED resistor, or support part | Direct wire | Visually associates the support part with its target |
| Same signal used at several nearby locations on one sheet | Short wired trunk plus local labels where needed | Retains local topology without long detours |
| Long connection crossing unrelated circuitry | Local label at both ends | Reduces clutter while keeping scope restricted |
| Connection crossing a child-sheet boundary | Hierarchical label and matching sheet pin | Makes the sheet's interface explicit |
| Truly system-wide control, clock, reset, or status net | Global label, used deliberately | Global reach is intentional and visible by name |
| Power rail shared across the design | Standard power symbol with an unambiguous rail name | Communicates power semantics and global scope |
| Off-board or external-interface signal | Connector pin plus visible net name and direction/context | Lets reviewers trace the boundary and harness meaning |
| Related indexed/grouped signals | Bus plus explicitly named members | Reduces repeated graphics while preserving member identity |
| Net exists solely to avoid drawing a 5–20 mm wire | Direct wire | A label would hide a relationship without reducing meaningful clutter |

### 3.2 Non-negotiable connection policies

- Do not create “label soup”: a page of components whose pins terminate almost entirely in
  detached labels is electrically compact but visually opaque.
- Do not draw wires across unrelated blocks merely to avoid labels.
- Prefer local over global labels unless cross-sheet global reach is required.
- Prefer hierarchical labels over global labels for normal parent/child interfaces.
- Place a label's connection point exactly on the intended pin or wire end and keep it on the
  connection grid.
- Give every meaningful signal a descriptive, stable name. Avoid unnamed long nets and
  generic names such as `NET1`, `SIG`, or `DATA` when the function is known.
- Use consistent active-low notation and polarity naming. KiCad's KLC requires the pin
  electrical type and inversion notation to agree with the datasheet; see
  [KLC S4.4](https://klc.kicad.org/symbol/s4/s4.4/).

### 3.3 Labels must preserve direction and context

A label name should reveal what travels on the net, not merely where it was first drawn.
For interfaces, use a consistent family such as `CAN_TX`, `CAN_RX`, `I2C_SCL`, `I2C_SDA`,
`MOTOR1_PWM`, or `DISP_DIGIT_SEL[0..5]`. Keep naming perspective consistent throughout the
design; avoid naming the same logical signal from opposite endpoint perspectives.

Where signal direction is important, set hierarchical label and sheet-pin shapes correctly
and validate that corresponding shapes match. KiCad's Sync Sheet Pins tool checks names and
graphic directions for matching sheet interfaces.

## 4. Component organization inside a block

### 4.1 Central device and pin function

Place the principal IC or active device near the center of its functional block. Arrange
connections around its functional pin groups rather than around physical package order.
Official KiCad symbols follow this principle: related interfaces such as SPI and UART are
grouped; positive power is above, ground below, inputs/control left, and outputs right.

If a library symbol's physical pin ordering makes a schematic unnecessarily difficult to
read, use a correct functional symbol rather than compensating with tangled wires. Symbol
pin names, numbers, and electrical types must still match the datasheet. The KLC expressly
states that functional grouping produces cleaner routing and easier-to-understand symbols.

### 4.2 Support components stay with their function

Place these parts beside the pin or sub-function they serve:

- decoupling and bypass capacitors;
- pull-ups and pull-downs;
- bias, gain-setting, timing, calibration, and bootstrap components;
- series damping and termination resistors;
- crystal/resonator networks;
- protection, filtering, and common-mode components;
- indicator LEDs and their resistors;
- test points and configuration straps.

Do not collect all capacitors or resistors in remote rows merely because they share a
reference prefix or power net. That hides association and makes review harder.

First-party schematic checklists support this function-by-function review. TI requires,
for example, per-supply-pin decoupling plus bulk capacitance in the
[TUSB4020BI checklist](https://www.ti.com/lit/an/slla408/slla408.pdf), and its
[level-translator checklist](https://www.ti.com/lit/an/spradm1/spradm1.pdf) separately checks
supply biasing, decoupling, sequencing, control pins, I/O constraints, and unused pins.
Microchip similarly requires verification of decoupling for each supply group, power
filtering, grounding, unused pins, and source capacity in its
[official checklist](https://onlinedocs.microchip.com/oxy/GUID-F9D3C532-E5D3-4B0B-A493-339C2C2521E2-en-US-1/GUID-2A14ABC0-2AB3-4120-873A-E198B8A56337.html).

Schematic proximity does not replace the PCB requirement for physical proximity. When a
component has a placement-sensitive requirement, add a concise note or property such as
`PLACE C17 ADJACENT TO U3 PIN 8`. IPC-2612's public scope explicitly includes critical
layout areas and other implementation restrictions in schematic documentation.

### 4.3 Decoupling presentation

**Konnect house rule:** Show each required decoupler with the device or supply-pin group it
supports. For ICs with many rails, a clearly titled `POWER AND DECOUPLING` sub-block on the
same sheet is acceptable if each capacitor is traceably associated with a rail or pin group.
Do not hide required decoupling behind an unexplained bank of capacitors.

Distinguish local high-frequency decoupling from rail-level bulk capacitance by placement,
value, and optional note. Where the manufacturer requires one capacitor per supply pin, the
schematic must make that multiplicity reviewable.

### 4.4 Connectors and external interfaces

- Put external inputs toward the left or top boundary and outputs toward the right boundary,
  unless the product's physical or functional narrative calls for another consistent order.
- Show connector pin numbers and functional signal names.
- Place protection and conditioning between the connector and internal circuitry so the
  boundary path is visible.
- Identify external voltage levels, expected direction, and special cable/shield/chassis
  connections where relevant.
- Avoid rotating connectors solely to make wires shorter if doing so reverses the page's
  overall flow.
- Show unused connector contacts and intentional no-connects explicitly.

### 4.5 Passives and discrete paths

Passives should be oriented so their role is obvious:

- series elements lie in the signal path;
- pull-ups rise toward the positive rail;
- pull-downs descend toward ground;
- dividers read as a vertical or horizontal chain with the sense node visibly branching;
- RC filters show the series/shunt topology directly;
- LED polarity and current-limiting resistor remain in one visible path;
- transistor/MOSFET bias and gate/base resistors remain adjacent to the controlled device.

Using labels between every element of these small networks is prohibited because topology,
not merely connectivity, is the information a reader needs.

### 4.6 Unused pins and units

Use KiCad no-connect flags only on pins intentionally left unconnected. KiCad's ERC treats an
unconnected pin without a flag as an error and warns if a no-connect flag is itself
unattached or placed on a connected pin. Do not leave ambiguous open pins.

For multi-unit symbols, place all used units in their relevant blocks and account for every
unused unit according to the device datasheet. Power units must be visible and connected.
The symbol definition must not hide pins that the datasheet requires the designer to connect;
see [KLC S4.5](https://klc.kicad.org/symbol/s4/s4.5/).

## 5. Junctions, crossings, and wire geometry

### 5.1 Grid and connection integrity

KiCad recommends a 50 mil grid for symbols, pins, and wires because connections require wire
ends and pins to coincide. Smaller grids are intended for text and symbol graphics, not
electrical connection points. Therefore:

- place electrical objects on the 50 mil connection grid;
- use orthogonal 90-degree wires by default;
- use 45-degree wiring only when it materially improves a special diagram and remains
  unambiguous;
- never use graphical lines as substitutes for wires;
- treat visible unconnected-end markers as a defect unless intentional and explained.

See KiCad's [grid and snapping guidance](https://docs.kicad.org/master/en/eeschema/eeschema.html#grids-and-snapping).

### 5.2 Crossing and junction policy

**Konnect house rule:** Avoid four-way wire junctions. Prefer a staggered pair of T-junctions
or a simpler trunk-and-branch drawing. Minimize unconnected wire crossings; use labels or
rearrange the block when crossings accumulate.

Every connected branch must be visually confirmed by a junction dot where KiCad requires
one. Every crossing without a dot must be intentionally unconnected. KiCad can optionally
render hop-overs, but the drawing should remain unambiguous without relying on a viewer's
particular hop-over setting. KiCad documents configurable hop-overs and junction-dot sizes in
[schematic formatting](https://docs.kicad.org/master/en/eeschema/eeschema.html#schematic-formatting).

### 5.3 Wire-quality checks

Reject or re-layout any block containing:

- wires through symbol bodies, reference fields, values, notes, or labels;
- avoidable backtracking or rectangular detours;
- stacked coincident wires used to mask duplicate routes;
- tiny stubs whose purpose is only to host a label;
- labels placed on crossings or junctions where their attachment is unclear;
- isolated wire fragments, dangling ends, or junction dots without a real branch;
- visually parallel nets so close that their labels or destinations become ambiguous.

## 6. Power symbols, domains, and grounding

Power symbols are global nets in KiCad. This is convenient but can silently connect distant
parts of a hierarchy, so they require stricter naming and review than local labels.

Use explicit rail names that preserve domain and voltage, for example `+24V_BAT`, `+5V_SYS`,
`+3V3_MCU`, `+3V3_A`, `VREF_2V5`, `GND`, `AGND`, or `CHASSIS`. Do not use visually similar
names for electrically distinct domains.

At each conversion or isolation boundary:

- draw input protection/filtering, converter, output filtering, and feedback in path order;
- name both sides of the boundary;
- show ground-domain relationships explicitly;
- add net ties or intended single-point connections as actual components where required;
- identify chassis, shield, protective earth, analog ground, and digital ground distinctly.

Use `PWR_FLAG` only when the net is truly driven but KiCad cannot infer that fact, such as a
supply entering through a passive connector. It is not a workaround for an incorrectly typed
power source or an undiagnosed power-path problem.

Avoid hidden power-input pins in new custom symbols. KiCad connects them implicitly to a
same-named global net and explicitly warns that this can create unintended connections;
visible power pins keep the design's power intent reviewable. See KiCad's
[hidden-power-pin documentation](https://docs.kicad.org/master/en/eeschema/eeschema.html#hidden-power-pins).

## 7. Buses and repeated channels

### 7.1 Buses

KiCad buses group related signals to simplify complicated designs. Vector buses represent
indexed nets such as `DATA[0..7]`; group buses represent named members such as
`USB1{DP DM}`. A bus entry is graphical and does not establish connectivity by itself. Every
member still needs a correctly attached wire and label. See KiCad's
[bus documentation](https://docs.kicad.org/master/en/eeschema/eeschema.html#buses).

Use a bus when:

- signals form a genuine functional family;
- member naming is systematic and visible;
- the bus removes repeated parallel graphics;
- the member breakout remains readable at each endpoint.

Do not use a bus to conceal unrelated signals, to replace a simple two-wire interface, or to
avoid planning the page. Label every member consistently and verify bus aliases/groups do
not create surprising net names.

### 7.2 Repeated channels

Prefer a reusable hierarchical subsheet when a channel is electrically identical and has a
stable interface. KiCad explicitly supports using the same subsheet multiple times and ships
an official multichannel demo. For reusable fragments across projects, KiCad's
[design blocks](https://docs.kicad.org/master/en/eeschema/eeschema.html#design-blocks)
can store schematic fragments and optional matching PCB layout fragments.

Every instance must have:

- a unique sheet/instance name and reference-designator set;
- predictable channel-indexed interface names;
- identical sheet-pin order and direction;
- clearly separate per-channel nets where separation is intended;
- explicit shared rails or controls where sharing is intended.

If channels differ materially, draw them as separate named variants rather than concealing
differences inside an apparently identical repeated sheet.

## 8. Text, annotation, and visual hierarchy

### 8.1 Required visible information

At minimum, the final schematic should visibly provide:

- unique reference designators;
- meaningful component values or part numbers;
- functional block titles;
- readable net and interface names;
- connector pin numbers and purpose;
- intentional DNP and no-connect state;
- important polarity, voltage, tolerance, rating, configuration, and layout notes;
- sheet title, revision, and page identity where the project uses a title block.

KiCad requires unique reference designators and supports sheet-based annotation numbering.
The KLC requires visible reference and value fields and device metadata such as footprint and
datasheet association for fully specified symbols; see
[KLC S6.2](https://klc.kicad.org/symbol/s6/s6.2/).

### 8.2 Text discipline

- Use short, declarative block titles and notes.
- Keep capitalization, units, prefixes, polarity, and net-name syntax consistent.
- Do not overlap fields or place them on wires.
- Keep reference and value adjacent to their symbol without obscuring pins.
- Use notes to capture intent that connectivity cannot express, especially placement,
  safety, voltage-domain, strap, and assembly requirements.
- Do not annotate the obvious. Text should explain purpose, constraints, or exceptions.

Use graphical headings and whitespace to identify blocks; use hierarchy to establish actual
interfaces. A decorative box is never a substitute for a sheet boundary or net scope.

## 9. Objective review and acceptance checks

The checks below are proposed Konnect acceptance criteria. They turn visual quality into a
repeatable workflow without pretending that aesthetics can be fully automated.

### 9.1 Machine-checkable electrical and document checks

- ERC reports zero unexplained errors and zero unexplained warnings.
- Every symbol is annotated; no reference contains `?`.
- Every required physical component has an assigned, valid footprint.
- Every required datasheet/part field is populated according to project policy.
- No new custom symbol relies on hidden power pins.
- No pin, wire end, or label attachment is off the connection grid.
- No unintended dangling wire, unattached label, or unattached no-connect flag exists.
- Every unused pin is deliberately handled.
- Every power-input net is driven by a real power-output pin or a justified `PWR_FLAG`.
- Every hierarchical label has a matching sheet pin with the same name and direction.
- No two distinct intended nets depend on ambiguous case-only name differences.
- All repeated-channel instances have complete and unique references/interfaces.
- The exported netlist and BOM contain the expected component and net counts.

### 9.2 Machine-checkable visual geometry checks

- No symbol-symbol, symbol-text, text-text, or label-text bounding boxes overlap.
- No wire passes through a symbol body or visible text.
- No junction dot exists without a connected branch.
- No connected branch lacks the required visible junction.
- No label sits ambiguously on a crossing.
- No functional block extends beyond the drawing frame.
- Reference and value fields are visible at the final review scale.
- Block headings do not collide with electrical objects.
- The root sheet exposes every intended child sheet and all interfaces match.

Automated geometry checks should report findings, not silently move objects, because an
automatic cleanup can change the intended visual hierarchy.

### 9.3 Human/rendered-image checks

Render every sheet to an image or PDF and inspect it independently of the editor object
model. Completion requires “yes” to all of these questions:

1. Can a reviewer identify the sheet's purpose and major blocks within several seconds?
2. Is normal signal/energy flow consistent and easy to follow?
3. Are power entry, conversion, and domains obvious?
4. Are support parts visibly associated with the device or interface they support?
5. Are topology-critical networks shown with wires rather than hidden behind labels?
6. Are long or cross-boundary connections labeled at the correct scope?
7. Are connector direction, pin purpose, and external voltage domain clear?
8. Are repeated channels obviously repeated and individually traceable?
9. Is the page readable at fit-to-page or normal review zoom?
10. Is there any cluster that requires tracing several unrelated labels simply to infer its
    function?

Any “no” blocks completion even if ERC passes.

### 9.4 Review sequence

Use this order so later validation does not mask earlier design problems:

1. Validate the functional and page plan.
2. Build one block.
3. Validate that block's electrical connections.
4. Render and inspect that block's layout.
5. Add the next block and its interface.
6. Repeat until every sheet is complete.
7. Run whole-design ERC and hierarchy/interface checks.
8. Export all rendered sheets and perform the communication review.
9. Perform a cleanup-only pass that preserves connectivity.
10. Re-run ERC, netlist comparison, and rendered review after cleanup.

## 10. Mapping into future Konnect skills and agents

No skills or agents are changed by this report. The eventual implementation should map the
findings as follows.

### 10.1 Schematic skill: mandatory workflow

Add explicit phases:

1. **Architecture:** identify blocks, interfaces, rails, repeated channels, and sheet plan.
2. **Notation policy:** choose wires, local labels, global labels, hierarchical labels, buses,
   and power symbols before bulk placement.
3. **Block construction:** place principal device, local support circuitry, and connectors one
   functional block at a time.
4. **Block review:** run connectivity checks and inspect a render after each block.
5. **Whole-design review:** run ERC, hierarchy checks, field/footprint checks, and rendered
   visual acceptance.
6. **Cleanup:** allow coordinate/orientation/text/wire cleanup only, then verify that netlist
   connectivity did not change.

### 10.2 Schematic-builder agent: required outputs

Before editing, return or record:

- functional-block list;
- page/hierarchy plan;
- named interface and rail list;
- repeated-channel plan;
- connection-notation decisions and exceptions.

At completion, return:

- per-sheet purpose and interface summary;
- ERC result with justified exclusions;
- footprint/field completeness result;
- rendered-sheet artifacts;
- visual-review checklist result;
- any deliberate exceptions to house rules.

### 10.3 Reviewer agent: independent responsibilities

The reviewer must not merely repeat ERC. It should inspect both the schematic object model
and rendered pages, then classify findings separately as:

- electrical correctness defects;
- scope/name/hierarchy defects;
- readability and flow defects;
- missing intent or documentation;
- implementation-sensitive requirements not captured for PCB layout.

The reviewer should fail a schematic with correct connectivity but poor visual communication.

### 10.4 Tooling gaps worth tracking

Future Konnect tooling would benefit from:

- rendered schematic screenshot/PDF generation per sheet;
- object bounding-box overlap detection;
- wire-through-symbol/text detection;
- label-scope inventory and global-label usage report;
- functional-block metadata or grouping support;
- hierarchy interface comparison;
- pre/post-cleanup netlist equivalence check;
- page-density and unreadable-cluster heuristics;
- traceability from each decoupler/support part to its served device or rail;
- a review artifact containing both ERC and visual acceptance results.

## 11. Compact house style proposed for approval

1. Plan function and hierarchy before placement.
2. Make each sheet tell one coherent story.
3. Draw normal flow left to right and power relationships top to bottom.
4. Use direct wires for local topology; use labels to cross distance or scope.
5. Use local labels by default, hierarchical labels at sheet interfaces, and global labels
   only for genuinely global nets.
6. Keep support components beside the function they support.
7. Use whitespace and headings to separate blocks; do not dump components into free space.
8. Use the 50 mil electrical grid, orthogonal wires, unambiguous T-junctions, and minimal
   crossings.
9. Make connectors, power domains, repeated channels, and special constraints explicit.
10. Require ERC, field/footprint completeness, and rendered visual review as separate gates.

## References

- KiCad, [Schematic Editor reference manual](https://docs.kicad.org/master/en/eeschema/eeschema.html)
- KiCad, [Library Convention](https://klc.kicad.org/)
- KiCad, [official demo projects](https://gitlab.com/kicad/code/kicad/-/tree/master/demos)
- IEC, [IEC 61082-1:2014](https://webstore.iec.ch/en/publication/4469)
- IEC TC 3, [Document and document kinds](https://tc3.iec.ch/tc-activity/current_document_kinds/)
- IEEE, [IEEE/ANSI 315-1975](https://standards.ieee.org/ieee/315/515/)
- IPC, [IPC-2612 official table of contents and scope](https://www.ipc.org/TOC/IPC-2612.pdf)
- IPC, [Document revision table](https://www.ipc.org/ipc-document-revision-table)
- Texas Instruments, [TUSB4020BI Schematic Checklist](https://www.ti.com/lit/an/slla408/slla408.pdf)
- Texas Instruments, [Schematic Checklist for Fixed/Direction-Control Translators](https://www.ti.com/lit/an/spradm1/spradm1.pdf)
- Microchip, [Schematic Checklist](https://onlinedocs.microchip.com/oxy/GUID-F9D3C532-E5D3-4B0B-A493-339C2C2521E2-en-US-1/GUID-2A14ABC0-2AB3-4120-873A-E198B8A56337.html)
