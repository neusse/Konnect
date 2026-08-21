# Claude workflow guidance gaps in Konnect v0.6.1 — proposed roadmap

> [!IMPORTANT]
> This is a Codex-assisted evaluation of the Claude-facing guidance published with
> Konnect v0.6.1. It is based on the exact tagged source, upstream issues and
> discussions, and an actual end-to-end **Codex** Konnect/KiCad benchmark. It is
> not a direct Claude benchmark and not a maintainer-authored compatibility claim.
>
> This report audits instructions, orchestration, and safety gates rather than
> proposing a second implementation stack. Every recommendation keeps Konnect's
> Rust-only direction, uses Konnect MCP tools and supported KiCad IPC for design
> mutation, and avoids Python and direct editing of KiCad source files.
> Freerouting is treated as Konnect's official whole-board routing direction,
> not as an optional competing workflow.

## Pinned scope

- **Published release:** [v0.6.1](https://github.com/mixelpixx/Konnect/releases/tag/v0.6.1), published 2026-08-17.
- **Tag commit:** [`506abe094204c6d4acd77415892e9e0e8fdb35fb`](https://github.com/mixelpixx/Konnect/commit/506abe094204c6d4acd77415892e9e0e8fdb35fb).
- **Claude package audited:** the six skills, two agents, and one `PreToolUse`
  hook embedded in the [v0.6.1 manifest](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/src/manifest.rs#L33-L129).
- **Runtime evidence:** [end-to-end benchmark discussion #239](https://github.com/mixelpixx/Konnect/discussions/239)
  and the [maintainer's source-level confirmation](https://github.com/mixelpixx/Konnect/discussions/239#discussioncomment-18046467).
- **Current release issues used as evidence:**
  [#240](https://github.com/mixelpixx/Konnect/issues/240),
  [#249](https://github.com/mixelpixx/Konnect/issues/249),
  [#250](https://github.com/mixelpixx/Konnect/issues/250), and
  [#253](https://github.com/mixelpixx/Konnect/issues/253).

The audit is intentionally limited to assets shipped in v0.6.1. At the time of
review, upstream `main` was 21 commits ahead of the tag; those post-release
fixes and PRs, the standalone `konnect-codex` companion, and the retired
KiCAD-MCP-Server are not treated as released Konnect capabilities.

## Executive assessment

The published Claude material is useful and materially better than raw MCP tool
descriptions. It teaches protected-file discipline, on-demand toolset loading,
revision-checked schematic-to-PCB transfer, basic layout order, ERC/DRC, and a
manufacturing checklist.

The remaining gap is not primarily more electrical-design prose. Claude needs a
deterministic operating procedure with observable gates. Today it can select a
valid tool but still choose the wrong sequence, trust contradictory evidence,
route a whole board with obstacle-blind L-bends, continue after losing the live
board, or approve a result whose artifacts disagree with the tool response.

The recommended target is five cooperating roles backed by shared skills:

1. library builder when a custom part is required;
2. schematic builder for complete circuit construction;
3. PCB builder as the sole live-board owner through placement and Freerouting;
4. independent design reviewer after mutation stops; and
5. read-only firmware/bring-up planner after review.

Run these roles sequentially for a single project. In particular, do not split
Freerouting into a concurrent routing agent: one PCB builder should own the live
KiCad document and its IPC session from placement checkpoint through route
acceptance.

## What v0.6.1 already does well

- The top-level skill establishes a clear integrity boundary: use Konnect for
  modifications and refuse ad hoc KiCad source edits. It also teaches dynamic
  tool discovery rather than hard-coding a tool count. See the
  [`konnect` skill](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/assets/skills/konnect/SKILL.md#L8-L38).
- The PCB skill correctly requires a dry-run, reviewed diagnostics, the exact
  returned plan revision, and one transactional IPC apply for
  `update_pcb_from_schematic`. See the
  [layout sequence](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/assets/skills/kicad-pcb/SKILL.md#L59-L79).
- The review skill escalates from structural checks to ERC/DRC and design audits,
  and the manufacturing skill requires DRC before export.
- The two agents have narrow Konnect tool access, bounded turns, and focused
  responsibilities. Those are good foundations for deterministic delegation.
- v0.6.1 itself demonstrates the right server-side safety philosophy: it maps
  every representable KiCad 10 footprint layer and refuses an unrepresentable
  one before IPC submission rather than hoping KiCad accepts it. The
  [release notes](https://github.com/mixelpixx/Konnect/releases/tag/v0.6.1)
  document the reproduced crash and the fail-closed repair.

## Prioritized workflow gaps

| Priority | Gap | Why guidance matters |
|---|---|---|
| P0 | Freerouting-first PCB workflow and PCB-builder agent | The released PCB skill calls `route_pad_to_pad` the primary router even though it is an obstacle-blind L-bend and Freerouting is the advertised direction. |
| P0 | Live-board identity and ownership gate | The hook is advisory, covers only part of the mutation surface, and cannot prevent the stale-file case documented in #240. |
| P0 | Evidence hierarchy and fail-closed review | The benchmark produced `LOOKS GOOD`/`READY` while direct DRC still had 25 errors and one unrouted item. Contradictory results need a defined authority order. |
| P0 | Datasheet-to-symbol-to-footprint acceptance | Generic pin-number conventions are not proof for a real manufacturer/package suffix, especially for circular, mirrored, socketed, or unusual parts. |
| P1 | Visual placement acceptance | “Verify placement” and “check courtyards” are advice, not a reviewable pre-route gate. |
| P1 | Incremental/ECO preservation workflow | Dry-run sync is strong, but the skill does not baseline accepted placement/routing or restrict rework to affected nets. |
| P1 | Power, thermal, and noisy-load branch | A generic trace-width table cannot validate batteries, motors, converters, fault energy, or return-current paths. |
| P1 | Deterministic agent routing and shared skill loading | The installed skills never name the installed agents, and the agents do not preload the corresponding skills. |
| P1 | Repeatable evidence package | A Markdown verdict without raw ERC/DRC, inventories, renders, routing provenance, and waivers is difficult to audit or reproduce. |
| P2 | Firmware handoff and staged bring-up | A manufacturable board still needs GPIO, boot/reset, test-point, rail, and proof-of-life planning. |
| P2 | Legacy/through-hole/manual-assembly sourcing | The manufacturing guidance is JLCPCB-centered and does not cover sockets, surplus parts, lead tolerances, hand soldering, or replaceability. |

## P0-1: make Freerouting the explicit whole-board route path

### Evidence

Konnect advertises Freerouting in the
[README](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/README.md#L13-L19)
and registers `autoroute` as DSN export, Freerouting, and SES import in the
[`integration` toolset](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect-core/src/tools/integration.rs#L128-L149).
However, the v0.6.1 handler
[always returns unavailable](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect-core/src/tools/integration.rs#L999-L1011).
Meanwhile, the PCB skill describes
[`route_pad_to_pad` as the primary routing tool](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/assets/skills/kicad-pcb/SKILL.md#L111-L137).
The benchmark proved that the installed KiCad Freerouting ActionPlugin could
complete an autonomous route, while also proving that imported widths and
clearances still needed explicit acceptance checks. Issue
[#253](https://github.com/mixelpixx/Konnect/issues/253) records the capability
and discovery mismatch.

### Guidance change

Add a `kicad-pcb-builder` agent and a progressively disclosed Freerouting
reference under the PCB skill. The default whole-board sequence should be:

1. prove exact live-board identity and save a component/pad/net/rule inventory;
2. complete the visual placement checkpoint;
3. verify outline, keepouts, stackup, netclasses, differential constraints, and
   unfilled/intentional zone state;
4. probe **engine availability** and **KiCad DSN/SES bridge availability** as
   separate capabilities;
5. route with Freerouting when the bridge is operational;
6. compare the returned board with the checkpoint; and
7. run direct DRC, short, width/clearance, trace/via, and unrouted checks before
   accepting the route or filling zones.

Keep `route_trace`, `route_pad_to_pad`, and `add_via` for deliberate short links
and understood local repairs. Do not present repeated L-bends as a substitute
for a whole-board router with obstacle avoidance and rip-up/retry.

### Rust/IPC implementation boundary

Konnect's Rust code may discover a standalone JAR or the engine bundled in the
KiCad plugin and may launch the Java process. Board identity, DSN export, SES
import, refresh, and result verification must use a supported KiCad IPC or
in-editor contract. If the installed KiCad IPC version does not expose that
exchange, return a structured `bridge_unavailable` capability and hand off the
smallest explicit step to the official KiCad ActionPlugin. Do not add a Python
bridge and do not parse or rewrite `.kicad_pcb` as a routing workaround.

### Acceptance criteria

- Guidance never calls obstacle-blind L-bends “autorouting.”
- Capability output distinguishes “Freerouting engine found” from “end-to-end
  KiCad bridge ready.”
- Route import is accepted only when board identity and component/pad inventory
  are unchanged, required connections are routed, widths/clearances satisfy the
  loaded rules, and direct DRC has no unwaived errors.
- If no safe Rust/IPC bridge exists, the workflow stops at a saved checkpoint
  and gives the ActionPlugin handoff instead of improvising another writer.

## P0-2: enforce one live board and fail closed after IPC loss

### Evidence

The released hook only prints an instruction before a subset of PCB tools; its
[matcher](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/src/manifest.rs#L121-L129)
does not cover the complete mutation surface, including schematic-to-PCB update
and several component/zone operations. It also does not make an IPC or board-path
decision. Issue [#240](https://github.com/mixelpixx/Konnect/issues/240) documents
the released fallback editing a stale saved board immediately after KiCad had
held and then lost that board.

### Guidance and Rust change

- The router skill must assign exactly one PCB-building agent as live owner.
- Before every PCB mutation phase, query the open document through IPC and prove
  that its canonical path equals the requested board.
- Expand hook coverage to every live PCB mutator.
- Replace advisory-only output with a Rust `PreToolUse` preflight that consumes
  the hook input and returns a structured deny when identity or liveness cannot
  be proven. Claude Code officially supports a
  [`PreToolUse` deny decision](https://code.claude.com/docs/en/hooks#pretooluse).
- Keep the server-side guard authoritative. The hook improves the client
  experience but must not be the only protection against stale IPC state.
- Once a server has observed a board live, an unexpected IPC loss closes the
  mutation phase. Reopen, re-identify, re-inventory, and resume from the last
  saved gate.

### Acceptance criteria

- No PCB mutation runs against a board whose active IPC document path differs
  from the tool input.
- An editor crash or IPC loss never silently switches the same phase to a saved
  file fallback.
- The hook covers all registered PCB mutators and names the exact recovery step
  in its denial.
- Reconnection invalidates placement and routing checkpoints until the board is
  saved and re-inventoried.

## P0-3: define evidence authority and make incomplete coverage visible

### Evidence

The benchmark's direct KiCad DRC reported 25 errors and one unrouted connection,
while `run_design_review` returned `LOOKS GOOD`, `validate_for_manufacturing`
returned `READY`, and review coverage reported zero pads on a populated board.
The maintainer
[confirmed the fail-open paths and their causes](https://github.com/mixelpixx/Konnect/discussions/239#discussioncomment-18046467).
The same run found `find_orphan_items` declaring every valid pin-mounted label
floating; an attempted “repair” created a real short. Issue
[#249](https://github.com/mixelpixx/Konnect/issues/249) documents the divergent
connectivity model.

The packaged prose compounds that uncertainty. The review skill describes its
shortcut as a comprehensive substitute, although the tagged shortcut did not
consume direct ERC/DRC evidence. The schematic builder's result template reports
an ERC outcome even though its workflow neither loads the export toolset that
owns ERC nor runs ERC. An agent must never be prompted to fill a success field
for evidence its prescribed sequence did not collect.

### Guidance change

Teach an explicit authority order:

1. exact design requirements and manufacturer datasheets;
2. KiCad's direct ERC/DRC and saved/exported connectivity;
3. direct Konnect short, net, pad, trace, and unrouted inventories;
4. aggregate review/manufacturing summaries; and
5. heuristic orphan/best-practice findings.

A weaker result may add a question; it must not override stronger contradictory
evidence or trigger automatic geometry changes. Any required check that fails to
run, returns structurally impossible coverage, or disagrees with direct evidence
makes the verdict **INCOMPLETE**, not clean.

Also make the review agent's universal “quality bars” conditional engineering
defaults. The current agent makes ESD on every external interface and bulk
capacitance on every rail unconditionally critical. Requirements and datasheets
should decide whether a default applies; the reviewer should record the evidence
rather than turn a useful heuristic into a universal rule.

### Acceptance criteria

- A board with any unwaived DRC error or required unrouted item cannot receive a
  ready verdict.
- Zero pads on a populated board, a missing artifact, or a failed required tool
  produces `INCOMPLETE` with the missing coverage named.
- A known weaker checker cannot cause an automated “fix” when ERC, short
  detection, and net connectivity disagree with it.
- Every waiver records rule, scope, reason, evidence, owner, and date.

## P0-4: require a physical custom-part pin map

### Evidence

The library skill includes useful mechanics, but its generic
[pin-numbering table](https://github.com/mixelpixx/Konnect/blob/506abe094204c6d4acd77415892e9e0e8fdb35fb/crates/konnect/assets/skills/kicad-library/SKILL.md#L54-L66)
states fixed BJT and MOSFET number orders that are not universal manufacturer
pinouts. Its custom IC workflow says to create from the datasheet but does not
require proof that each physical lead, symbol pin, and footprint pad is the same
electrical node. This is especially risky for bottom views, circular packages,
tubes/displays, connectors, mirrored parts, and replaceable sockets.

### Guidance change

Add a `kicad-library-builder` agent and a custom-part acceptance reference. It
must record one row per physical lead:

| Datasheet lead | Function | Symbol pin/name/type | Footprint pad | X/Y | Drawing view/direction | Evidence |
|---|---|---|---|---|---|---|

Require an explicit top/bottom/component/pin-side declaration, a walk from the
manufacturer's key in the documented direction, exact part/package suffix, and
a query-back plus visible disposable placement before the part enters a real
schematic.

### Acceptance criteria

- Lead, symbol-pin, and electrical-pad counts reconcile, with every exception
  documented.
- Every number occurs exactly once unless the datasheet explicitly joins leads.
- Pin type, polarity, common connection, drill, pitch, body, tolerance, and
  physical viewing direction are verified.
- Any unexplained mirror, reversal, duplicate, missing lead, or view ambiguity
  blocks use and receives an independent review.

## P1 workflow branches

### Visual placement acceptance

The released skill says to check courtyard overlaps and verify moves, but it has
no artifact or checkpoint. Before routing, require a saved board inventory, a 2-D
render showing outline, pads, holes, courtyards and references, direct overlap and
edge checks, and an exception list. A 3-D render is additional evidence, not a
substitute for copper/courtyard inspection. Any placement change or IPC ownership
change invalidates the checkpoint.

**Accept when:** no blocking pad/hole/courtyard/edge/access conflict remains and
the rendered placement is explicitly approved for routing.

### Incremental/ECO preservation

Extend the strong revision-checked sync procedure with a baseline of references,
positions, pads, traces by net/layer, vias, zones, and DRC. Review the dry-run
delta; apply only the exact plan revision; prove unaffected placement and routing
did not change; identify affected nets; and reroute only those nets when possible.
Use whole-board Freerouting only when the change invalidates the global route.

**Accept when:** the before/after report accounts for every change and preserves
all unaffected approved board state.

### Power, thermal, and noisy-load layout

Trigger a separate reference for batteries, motors, heaters, solenoids,
converters, and other high-current or high-`di/dt` loads. Establish min/nominal/
transient/reverse voltage, continuous/peak current, copper weight, temperature
rise, voltage-drop allowance, fault energy, connector/fuse ratings, and return
paths. Size copper from those inputs and separate noisy returns from MCU, IMU,
analog, and oscillator references.

**Accept when:** the report states assumptions and calculated drop/loss at
continuous and peak current, verifies protection placement and component ratings,
and leaves no unbounded current or shared sensitive/noisy return path.

### Repeatable review evidence

Create a timestamped evidence directory outside protected KiCad source files.
Include raw ERC/DRC, connectivity/short/orphan output, component/pad/trace/via/net
inventories, placement render, route provenance and DSN/SES identity, manufacturing
artifact list with sizes/hashes, custom-part maps, waivers, and the final verdict.
Record failed or unavailable checks instead of omitting them.

**Accept when:** another reviewer can reproduce the verdict from the saved
evidence without trusting a prose summary or an in-memory tool response.

## P2 handoff branches

### Firmware and bring-up planner

Add a read-only `kicad-bringup-planner` agent after independent review. It should
produce a GPIO table, reset/boot/programming behavior, safe startup states, test
point expectations, current-limited first-power sequence, rail checks,
proof-of-life behavior, stop conditions, and interface/load enable order. It must
not modify the board or energize hardware.

### Legacy and manual assembly

Add a conditional manufacturing reference for through-hole, socketed, surplus,
or hand-assembled parts: exact suffix, lifecycle/source/date, alternates,
lead/drill/pitch/height/tolerance, polarity/key, socket dimensions, rework access,
stock attrition, and counterfeit/oxidation risk. A distributor listing alone is
not proof of active production.

## Make the agents actually share and use the skills

The six installed skills do not name either installed agent, so delegation is
left to the model. The package also installs nine reference files, but none of
the six parent `SKILL.md` files tells Claude when to read any of them. The agent
files duplicate condensed workflow rules rather than preloading the corresponding
skill. Claude's own documentation says a
subagent starts with an isolated context and supports a
[`skills` field to preload skill content](https://code.claude.com/docs/en/sub-agents#supported-frontmatter-fields).

Recommended orchestration:

| Branch | Agent | Preloaded guidance | Mutation ownership |
|---|---|---|---|
| Custom part required | `kicad-library-builder` | `konnect`, `kicad-library` | Library task only |
| Complete schematic build | existing schematic builder | `konnect`, `kicad-schematic` | Schematic phase |
| PCB transfer/layout/route | `kicad-pcb-builder` | `konnect`, `kicad-pcb` | Sole live PCB owner |
| Final independent audit | existing design reviewer | `konnect`, `kicad-review`, `kicad-manufacture` | Read-only during verdict |
| Firmware/first power | `kicad-bringup-planner` | bring-up reference plus review evidence | Read-only |

Add this routing table to the top-level `konnect` skill using clear trigger
conditions. Keep detailed procedure in the branch skills/references so there is
one source of truth rather than duplicated agent prose. Claude skills are loaded
on demand, so branch-specific material can remain behind precise descriptions;
see Anthropic's [skills documentation](https://code.claude.com/docs/en/slash-commands).

## Proposed implementation order

1. **Guidance-only safety PR:** correct the routing hierarchy, add evidence
   authority, add custom-part and placement gates, bind existing agents to their
   skills, and make agent delegation deterministic.
2. **Add three bounded agents:** library builder, PCB builder, and read-only
   bring-up planner. Keep one live PCB owner and one independent reviewer.
3. **Rust hook/server guard:** full mutator coverage, exact board identity, and
   structured denial on stale or lost IPC state.
4. **Rust Freerouting capability contract:** separate engine discovery from
   KiCad bridge readiness; use supported IPC when available and fail closed to
   the ActionPlugin checkpoint otherwise.
5. **Benchmark the guidance:** run a custom-part design, a dense placement, an
   ECO update, a power/noisy-load board, Freerouting import, independent review,
   manufacturing export, and bring-up handoff. Neuter each gate once to prove the
   test catches its absence.

## Boundaries

- No Python, SWIG, or alternate language backend.
- No manual or automated editing of `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`,
  `.kicad_sym`, `.kicad_mod`, or KiCad library tables outside Konnect's supported
  Rust/MCP operations.
- No GUI automation presented as a stable MCP contract. A user-run official
  Freerouting ActionPlugin step is an explicit handoff when IPC lacks the needed
  exchange, not a hidden fallback.
- No positive manufacturing verdict based only on a successful request or an
  aggregate summary. The saved result and direct KiCad evidence are authoritative.
- No parallel agents mutating the same project or sharing one live PCB IPC
  session.

## Bottom line

Konnect already exposes an unusually broad Rust/KiCad tool surface. That does not
remove the need for workflow guidance; it makes the guidance more important. An
AI needs to know which evidence is authoritative, when a phase is complete, when
to stop, and which specialist owns the next phase.

For v0.6.1, the highest-value change is not another generic design checklist. It
is a deterministic Claude workflow: validate custom parts, build and verify the
schematic, approve visible placement, route the complete board through
Freerouting, independently prove the result, package the evidence, and only then
prepare manufacturing and bring-up. That keeps Konnect's Rust/IPC architecture
clean while giving Claude enough direction to use it safely.
