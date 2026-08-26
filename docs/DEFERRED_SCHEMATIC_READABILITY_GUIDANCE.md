# Deferred: Schematic Readability Guidance and Agent Workflow

**Status:** Research complete; guidance implementation is deferred until the
current Konnect pull-request activity settles and the findings have been reviewed.

**Resume trigger:** Revisit before the next schematic-agent or skill revision,
and before treating another generated schematic as complete.

## Problem

Konnect can produce electrically correct schematics whose page layout is still
difficult to read. Components are often placed wherever space is available,
with too little functional structure, inconsistent signal flow, excessive or
insufficient wiring, and no deliberate visual hierarchy.

Electrical correctness is necessary, but it is not sufficient. A successful
schematic must communicate how the circuit works to a human reviewer.

## Research deliverable

Build source-backed guidance for excellent schematic communication. Capture the
findings in `docs/SCHEMATIC_READABILITY_GUIDANCE_RESEARCH.md`, then translate
the approved rules into the Konnect schematic skill and schematic-builder agent.

The research must address:

1. **Functional architecture**
   - partitioning a circuit into recognizable functional blocks;
   - arranging blocks in the order that power, signals, and control flow;
   - deciding when a design belongs on one page versus hierarchical sheets;
   - visually separating power entry, protection, conversion, controllers,
     interfaces, sensors, drivers, connectors, and repeated channels.

2. **Wires versus labels**
   - when a direct wire makes a relationship easier to understand;
   - when a local net label reduces clutter without hiding intent;
   - when global labels or power symbols are justified;
   - when hierarchical labels and sheet pins should define an interface;
   - when buses, bus entries, or repeated-channel notation improve clarity;
   - limits that prevent a schematic from becoming a collection of unrelated
     label flags with no visible circuit flow.

3. **Component organization**
   - left-to-right and top-to-bottom flow conventions;
   - consistent orientation of symbols and pins;
   - placement of decoupling capacitors, bias parts, pull-ups, protection,
     termination, and other support components near the function they serve;
   - treatment of connectors, test points, no-connect pins, and unused units;
   - grouping repeated circuits while keeping each channel traceable.

4. **Drawing clarity**
   - orthogonal wire routing and sensible spacing;
   - avoiding ambiguous crossings, unnecessary junctions, long detours, and
     wires through symbols or text;
   - reference/value visibility, useful notes, block titles, and interface
     descriptions;
   - page size, margins, grid use, whitespace, and density targets;
   - meaningful net names and consistent naming conventions.

5. **Human review and verification**
   - checks that distinguish electrically valid from understandable;
   - objective layout checks that an agent can perform;
   - rendered-image inspection after each major functional block and again at
     final review;
   - conditions that must block completion even when ERC passes.

## Guidance implementation requirements

The eventual skill and agent changes must:

- require a functional-block and page plan before placing symbols;
- require deliberate coordinates and spacing rather than automatic dumping;
- define a decision process for wires, local labels, global labels, and
  hierarchical labels;
- build and inspect one functional block at a time;
- preserve a visible power and signal narrative across the page;
- require rendered schematic inspection, not only tool-return success and ERC;
- permit a cleanup/re-layout pass that does not alter connectivity;
- explain every intentional exception to the normal readability rules.

## Minimum schematic completion gates

A generated schematic must not be reported as complete unless:

- a reviewer can identify the major functional blocks without tracing every
  individual net;
- normal signal flow is visually consistent and power flow is apparent;
- local wiring is used where it communicates relationships, while labels are
  used where wiring would create clutter or cross block/page boundaries;
- global labels are limited to genuinely global nets;
- hierarchical sheet interfaces are explicit when multiple sheets are used;
- support components are visually associated with the device or interface they
  support;
- there are no unintended wire crossings, ambiguous junctions, overlapping
  symbols/text, or unreadable dense clusters;
- connectors and external interfaces clearly identify direction and purpose;
- net names, references, values, and notes are readable and consistent;
- ERC, connectivity checks, and rendered visual review all pass independently.

## Expected artifacts

When this task resumes, produce:

1. the source-cited research report;
2. a compact schematic style guide suitable for agent instructions;
3. a wire-versus-label decision table;
4. a functional-block/page-planning template;
5. a schematic visual-review checklist;
6. updated Konnect schematic skill and agent guidance;
7. before-and-after examples demonstrating the same connectivity with materially
   better readability.

## Reminder

Do not accept a schematic merely because every component and net is present.
The drawing is an engineering communication artifact. If the circuit's structure
is not obvious from the rendered pages, the schematic workflow is incomplete.
