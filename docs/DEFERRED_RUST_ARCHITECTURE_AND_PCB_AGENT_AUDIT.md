# Deferred: Rust Architecture and PCB-Agent Workflow Audit

**Status:** Waiting for the current upstream pull-request activity to settle.

**Resume trigger:** Revisit this before attempting another broad PCB workflow fix
or benchmark, after the active Konnect PRs affecting PCB transfer, footprints,
layers, 3D models, routing, or agent guidance have either merged or closed.

## Why this is needed

Konnect is being changed at several layers without one authoritative view of how
the Rust implementation, exposed MCP commands, bundled PCB agent, and KiCad
interact. That makes it difficult to distinguish:

- functionality that exists and is used by the PCB agent;
- functionality that exists but is bypassed or unreachable;
- missing transformations, validation, or output checks;
- duplicated KiCad behavior implemented in Rust;
- failures caused by Konnect, agent guidance, KiCad, or the selected workflow.

The recent clock-board run was allowed to pass even though ordinary library
parts such as capacitors, resistors, and LEDs had no visible 3D bodies. That must
be treated as a failed workflow result, not merely a cosmetic observation.

## Required deliverable

Create a source-backed architecture package containing:

1. **Rust module map**
   - workspace crates and their responsibilities;
   - important modules, ownership boundaries, and dependencies;
   - KiCad IPC, CLI, file-format, library, routing, and export boundaries.

2. **Interaction and data-flow diagrams**
   - request from Codex/Claude agent to MCP tool registration and dispatch;
   - handler, service/core, mapper/serializer, KiCad, and response flow;
   - schematic-to-PCB transfer and footprint-library resolution;
   - footprint creation/update, 3D-model attachment, placement, routing,
     verification, rendering, and manufacturing export;
   - error, rollback, revision, dry-run, and fallback paths.

3. **Exposed-command inventory mapped to Rust code**
   - MCP toolset and command name;
   - schema and accepted inputs;
   - registration and handler location;
   - downstream Rust functions/modules;
   - KiCad IPC/CLI/file operation used;
   - mutations and expected outputs;
   - validation, tests, known limitations, and failure modes.

4. **PCB-agent coverage matrix**
   - command is required, optional, or prohibited for each workflow phase;
   - command is explicitly invoked by the PCB agent/skills, merely available,
     or unused;
   - required preconditions and artifacts passed between phases;
   - expected postconditions and the check that proves each one;
   - gaps where the agent assumes behavior that the Rust tools do not provide.

5. **Native-KiCad versus Rust responsibility matrix**
   - identify behavior delegated to KiCad and behavior reimplemented in Rust;
   - explain why each reimplementation is necessary;
   - identify candidates for replacement by KiCad 11 headless/schematic IPC or
     a future noninteractive native update-PCB-from-schematic command;
   - document version-dependent fallbacks and capability detection.

6. **End-to-end PCB contract**
   - define what goes into the PCB workflow;
   - define the board, reports, images, and manufacturing artifacts that must
     come out;
   - define stop/fail conditions so incomplete boards cannot be reported as
     successful.

## Minimum PCB completion gates

A PCB workflow must not pass solely because commands returned success. At
minimum, verify:

- schematic-to-PCB reference, value, footprint, pad, and net correspondence;
- all expected footprints are present and placed without prohibited overlap;
- footprints retain library graphics and 3D-model references where the selected
  KiCad library footprint normally supplies them;
- the 3D viewer visibly contains ordinary modeled parts (including representative
  resistors, capacitors, LEDs, connectors, and modules when models exist);
- custom parts without models, such as the DR2000 when no model is available,
  are listed explicitly as justified exceptions;
- unrouted connections, shorts, DRC violations, courtyard collisions, board-edge
  violations, and unsupported-layer/lost-content warnings are reported;
- routing follows the approved strategy, including Freerouting when applicable;
- generated manufacturing outputs correspond to the final verified board
  revision.

Missing expected 3D bodies is a blocking diagnostic: inspect model references,
path-variable/library resolution, and whether Konnect synthesized or rewrote the
footprint instead of preserving the native library footprint. Do not waive the
failure without naming the affected references and proving that no model exists.

## Execution order after the PRs settle

1. Synchronize the local checkout and fork to the settled upstream revision.
2. Inventory all exposed tools directly from registration/schema code.
3. Trace each PCB-agent workflow instruction to actual commands and Rust paths.
4. Generate the diagrams and coverage matrices from that evidence.
5. Run focused contract tests for transfer, library preservation, and 3D models.
6. Re-run the clock-board benchmark only after the missing-path analysis is
   complete.
7. Convert confirmed gaps into narrowly scoped issues or PRs, with one owning
   layer and an observable acceptance test per change.

## Reminder

Do not resume by patching the next visible symptom. First establish the complete
command-to-code-to-KiCad map and the PCB-agent coverage matrix. The purpose of
this audit is to reveal missing or bypassed stages before more implementation
work is accepted.
