# Konnect MCP evaluation

> Archived from the review we published in
> [Konnect discussion #152](https://github.com/mixelpixx/Konnect/discussions/152#discussioncomment-17993229)
> on August 12, 2026. The wording below is preserved as the original evaluation;
> current follow-up work is tracked separately in
> [IMPROVEMENT_BACKLOG.md](IMPROVEMENT_BACKLOG.md).

## Scope of the comparison

The clock was rebuilt from an empty project using the same functional parts
and constraints as the earlier KiCad design. The earlier schematic and PCB
files were not exported, imported, parsed for coordinates, or used as source
design data. The only native KiCad GUI steps were the file-format operations
that Konnect/KiCad 10 cannot currently perform end-to-end: PCB synchronization
and Specctra DSN/session exchange for routing.

## What worked well

- The complete schematic is reproducible as code instead of being only a set
  of manual editor actions.
- Batch MCP calls made creation of the 42-symbol schematic, net labels,
  footprints, and annotations fast and auditable.
- A custom 18-pad HDLG-2416 through-hole footprint was created and registered
  through the API from the display dimensions.
- Live PCB placement through KiCad IPC was visible immediately and was easy to
  revise after physical-clearance feedback.
- Tool discovery allows an agent to request only the relevant KiCad operations
  instead of loading a large fixed interface.
- The JSONL logs provide a useful build trail for debugging and comparison.
- The resulting design is native KiCad data and passes KiCad's own ERC and DRC.

## Current limitations and friction

- Konnect did not automatically find this per-user KiCad installation's symbol,
  footprint, and 3D-model directories; the scripts set the KiCad 10 environment
  variables explicitly.
- The Codex process could not hot-load a newly registered MCP server, so this
  run used Konnect's actual stdio JSON-RPC interface directly. A new Codex task
  can use the registered server normally.
- The live KiCad IPC API uses a single default socket. If another PCB Editor
  instance owns it, live operations can target the wrong board or fail.
- Schematic-to-PCB synchronization was not available in the initial Konnect
  build path, requiring one native KiCad update-from-schematic operation.
- Konnect advertises autorouting, but KiCad 10 removed the command-line
  Specctra conversion path it expects. Routing therefore required KiCad's GUI
  DSN export/session import around Freerouting.
- Placement helpers do not replace mechanical review. Courtyard checks and
  user review were still needed to catch tight spacing and edge clearance.
- The mounting-hole helper produced graphics on an undefined layer in this
  version, which KiCad had to rescue to a valid user layer.
- Uncommon parts such as the 24CSM01 may need a generic numbered symbol or a
  new custom symbol before the design is presentation-perfect.
- A project-creation call can initialize design files, so rebuild scripts need
  clear safeguards against being run over a finished project.

## Bottom line

Konnect is strongest as a reproducible design-construction and inspection
layer around KiCad. It substantially reduces repetitive schematic and layout
work and leaves a useful audit trail. It does not yet remove the need for
native KiCad on KiCad 10: board synchronization, router interchange, mechanical
clearance review, and a few library/layer edge cases still require careful GUI
or command-line verification.
