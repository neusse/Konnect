# Konnect improvement backlog — 29-Aug-2026 (v0.11.0)

> **Disclosure.** This is a Codex-assisted evaluation based on the v0.11.0
> release and source, the roadmap and contribution rules, every currently open
> issue and pull request, relevant merged work, maintainer feedback in
> Discussions, and end-to-end KiCad use through the version-matched
> `konnect-codex` companion plugin. Priorities are recommendations, not
> maintainer assignments. Work should still be claimed on its issue, designed
> in public, and delivered as focused, tested PRs.

## Snapshot

- Released contract: [v0.11.0](https://github.com/mixelpixx/Konnect/releases/tag/v0.11.0),
  tag commit [`a22ad21`](https://github.com/mixelpixx/Konnect/commit/a22ad2153dcf45dbcf1cc63b5b0f1e40c93d7956).
- Current upstream `main`: [`bf60eb1`](https://github.com/mixelpixx/Konnect/commit/bf60eb1458b084c9f620ad37655dd272470d61d9),
  one package-metadata stamp beyond the release tag.
- Released surface: **20 toolsets, 217 registered tools, 223 total tools**.
- Live inventory on 29-Aug-2026: **31 open issues and 7 open pull requests**.

## Executive assessment

v0.11.0 is primarily a reliability release. It closes the library-refresh,
multi-unit, Windows discovery, startup side-effect, metadata-placement, and
Default-netclass defects that dominated the v0.10 backlog. It also adds
predefined router-size management, destructive graphics cleanup, resolved
netclass reporting, and explicit `held` feedback from placement planners.

The remaining highest-risk gaps are narrower and clearer:

1. project ownership can still escape to an unrelated ancestor (#189);
2. live-editor loss can still permit stale-file mutation (#240);
3. exported artifacts are not yet identity- and content-verified (#252); and
4. released Claude guidance can claim evidence it never collected (#357) and
   cannot surface hook output reliably (#358).

The maintainer-requested Freerouting bridge remains the largest active feature.
Its four PRs are still open and therefore must not be treated as shipped.

## What v0.11.0 changed

- Fixed official footprint refresh (#331), complete Default-netclass handling
  (#326), multi-unit resolution (#182), per-user Windows discovery (#254),
  non-mutating startup (#242), and Datasheet/Description placement (#226).
- Added `set_predefined_sizes` and `get_predefined_sizes`; router palettes are
  now distinct from DRC floors and netclass targets.
- Added `delete_graphics`, allowing deliberate replacement of generated
  outlines and other graphics instead of append-only accumulation.
- `get_netclasses` now reports resolved values plus `inherits` and
  `missing_fields`; `null` no longer automatically means an invalid class.
- Placement planners report a `held` set and honor KiCad-locked footprints.
  Mechanically constrained through-hole parts still must be explicitly locked;
  Konnect cannot safely infer enclosure intent from pad type alone.
- Guidance corrected unsafe pin-number assumptions, invalid library IDs, and
  LED polarity examples. Documentation count checks gained an `xtask` fixer.

## P0 — correctness and non-destructive behavior

### 1. Bound project ownership — #189

[#189](https://github.com/mixelpixx/Konnect/issues/189) can associate a loose
schematic with an unrelated ancestor project. Use depth-bounded, cycle-safe
sheet-tree membership, accept exactly one verified owner, and return a
structured conflict naming candidates when ownership is ambiguous. Path depth,
`$HOME`, and Git boundaries are not reliable ownership evidence.

### 2. Refuse stale-file mutation after live IPC loss — #240 / #241

[#240](https://github.com/mixelpixx/Konnect/issues/240) remains the central
wrong-state hazard. Bind mutators to the observed document identity and fail
closed when a formerly live editor disappears. The document-answering mock in
[#241](https://github.com/mixelpixx/Konnect/issues/241) is useful test support,
not the policy itself.

### 3. Verify every reported artifact — #252 / PR #270

[#252](https://github.com/mixelpixx/Konnect/issues/252) needs existence,
nonzero-size, signature, board/revision identity, and per-artifact evidence.
[PR #270](https://github.com/mixelpixx/Konnect/pull/270) conflicts with current
main and includes historical overlap. Replace it with a clean v0.11-based PR.

### 4. Make released guidance evidence-honest — #356 / #357 / #358

v0.11 incorporates the concrete library-ID and pin-rule corrections from
[#356](https://github.com/mixelpixx/Konnect/issues/356); verify and close that
issue rather than duplicating the fix. The broader problem remains:
[#357](https://github.com/mixelpixx/Konnect/issues/357) requires every skill
and agent to collect the evidence it claims, while
[#358](https://github.com/mixelpixx/Konnect/issues/358) requires a valid hook
matcher and visible, actionable hook output. These are workflow correctness,
not cosmetic documentation.

## P1 — high-value workflow reliability

### Freerouting: active four-PR stack

Merge and validate in dependency order:

1. [#338](https://github.com/mixelpixx/Konnect/pull/338) — revision-bound DSN
   export and reverse manifest.
2. [#339](https://github.com/mixelpixx/Konnect/pull/339) — strict SES planning
   and atomic IPC apply.
3. [#340](https://github.com/mixelpixx/Konnect/pull/340) — local Freerouting
   native-MCP orchestration, validation, timeouts, and cleanup.
4. [#342](https://github.com/mixelpixx/Konnect/pull/342) — optional,
   authenticated KiCad-native Specctra bridge with Rust fallback.

The stack passed a real Freerouting route on the previous baseline, but all four
PRs must be rebased and rerun against v0.11 before review. Until they merge and
ship, the companion's local bridge remains a compatibility layer.

### Other active reliability work

- [#328](https://github.com/mixelpixx/Konnect/issues/328): make connectivity
  bus-aware; keep KiCad ERC authoritative meanwhile.
- [#315](https://github.com/mixelpixx/Konnect/issues/315): implement real
  connected-wire movement; an explicit refusal remains safer than false success.
- [#103](https://github.com/mixelpixx/Konnect/issues/103): make the server own
  multi-session lifecycle and orphan cleanup. Companion cleanup mitigates Codex
  use but cannot fix core ownership.
- [#256](https://github.com/mixelpixx/Konnect/issues/256): open and prove the
  exact requested board document.
- [#257](https://github.com/mixelpixx/Konnect/issues/257): prepare the KiCad 11
  SWIG-removal and IPC transition.
- [#291](https://github.com/mixelpixx/Konnect/issues/291): honor or explicitly
  reject the requested SVG filename.
- [#305](https://github.com/mixelpixx/Konnect/issues/305): edit 3-D models on
  placed footprints now that the common refresh path is fixed.
- [#360](https://github.com/mixelpixx/Konnect/issues/360): carry downloaded
  catalog Datasheet/Description metadata into the internal lookup path; v0.11
  fixed library placement but not this separate catalog-ingestion gap.

## Open pull-request assessment

| PR | Current state | Assessment |
| --- | --- | --- |
| [#342](https://github.com/mixelpixx/Konnect/pull/342) | Clean before v0.11 | Fourth Freerouting layer; rebase after #338-#340 and rerun the real route. |
| [#340](https://github.com/mixelpixx/Konnect/pull/340) | Clean before v0.11 | Native MCP orchestration; rebase after #339. |
| [#339](https://github.com/mixelpixx/Konnect/pull/339) | Clean before v0.11 | Atomic SES import; rebase after #338. |
| [#338](https://github.com/mixelpixx/Konnect/pull/338) | Clean before v0.11 | DSN/export foundation; rebase first. |
| [#270](https://github.com/mixelpixx/Konnect/pull/270) | Conflicting | Replace with a focused current-main #252 PR. |
| [#268](https://github.com/mixelpixx/Konnect/pull/268) | Conflicting | Reassess remaining coverage against shipped validation work. |
| [#176](https://github.com/mixelpixx/Konnect/pull/176) | Conflicting, stale | POSIX reload is not a complete Windows/multi-instance lifecycle design. |

## Complete open-issue disposition

| Issue | Priority | Disposition |
| --- | --- | --- |
| [#360](https://github.com/mixelpixx/Konnect/issues/360) | P1 | Preserve catalog Datasheet/Description through ingestion and lookup. |
| [#358](https://github.com/mixelpixx/Konnect/issues/358) | P1 | Fix matcher and make hook evidence visible and actionable. |
| [#357](https://github.com/mixelpixx/Konnect/issues/357) | P0 | Make skill/agent claims match evidence actually collected. |
| [#356](https://github.com/mixelpixx/Konnect/issues/356) | Verify/close | Corrections appear in v0.11; confirm release behavior. |
| [#351](https://github.com/mixelpixx/Konnect/issues/351) | P2 | Define a lossless, explicit Edge.Cuts promotion workflow. |
| [#341](https://github.com/mixelpixx/Konnect/issues/341) | P1 active | Native DSN bridge in #342. |
| [#337](https://github.com/mixelpixx/Konnect/issues/337) | P1 active | Freerouting stack #338/#339/#340/#342. |
| [#328](https://github.com/mixelpixx/Konnect/issues/328) | P1 | Bus-aware connectivity. |
| [#325](https://github.com/mixelpixx/Konnect/issues/325) | P2 | Copilot subset is documented; protocol filtering remains separate. |
| [#315](https://github.com/mixelpixx/Konnect/issues/315) | P1 | Real connected-wire movement. |
| [#305](https://github.com/mixelpixx/Konnect/issues/305) | P2 | Placed-footprint 3-D model editing. |
| [#296](https://github.com/mixelpixx/Konnect/issues/296) | P2 | Focused symbol/footprint controls plus workflow guidance. |
| [#291](https://github.com/mixelpixx/Konnect/issues/291) | P1 | Correct SVG filename contract. |
| [#258](https://github.com/mixelpixx/Konnect/issues/258) | P1 | Batch custom-field upsert. |
| [#257](https://github.com/mixelpixx/Konnect/issues/257) | P1 deadline | KiCad 11 plugin/IPC migration. |
| [#256](https://github.com/mixelpixx/Konnect/issues/256) | P1 | Open and prove exact board identity. |
| [#252](https://github.com/mixelpixx/Konnect/issues/252) | P0 | Clean current-main artifact-verification PR needed. |
| [#241](https://github.com/mixelpixx/Konnect/issues/241) | P0 support | Shared document-answering mock for #240 tests. |
| [#240](https://github.com/mixelpixx/Konnect/issues/240) | P0 | Refuse stale fallback after observed-live IPC loss. |
| [#233](https://github.com/mixelpixx/Konnect/issues/233) | P1 | Linux loading/client reachability evidence. |
| [#225](https://github.com/mixelpixx/Konnect/issues/225) | P2 | Select footprint graphics by stable identity. |
| [#221](https://github.com/mixelpixx/Konnect/issues/221) | P1 | Make live-CI claims real and fix fixture/race behavior. |
| [#210](https://github.com/mixelpixx/Konnect/issues/210) | P2 | Reduce whole-sheet serialization diff churn. |
| [#189](https://github.com/mixelpixx/Konnect/issues/189) | P0 decision | Membership-based ownership plus structured conflict. |
| [#181](https://github.com/mixelpixx/Konnect/issues/181) | P3 | Preserve lock-name compatibility before sha2 bump. |
| [#154](https://github.com/mixelpixx/Konnect/issues/154) | P2 | Homebrew after signing/release artifacts stabilize. |
| [#131](https://github.com/mixelpixx/Konnect/issues/131) | P1 release | Sign/notarize both macOS slices and final artifact. |
| [#119](https://github.com/mixelpixx/Konnect/issues/119) | P1 | Bound and preserve complete DRC output. |
| [#118](https://github.com/mixelpixx/Konnect/issues/118) | P2 | True layer-aware 2-D plot. |
| [#103](https://github.com/mixelpixx/Konnect/issues/103) | P1 | Core multi-session ownership and orphan cleanup. |
| [#84](https://github.com/mixelpixx/Konnect/issues/84) | P1 | Finish structural parsing conversions. |

## Recommended execution order

1. Verify/close #356 and land a focused #357/#358 guidance series.
2. Rebase and merge Freerouting in stack order #338 → #339 → #340 → #342.
3. Implement the actual #240 policy with #241 evidence.
4. Replace #270 with a clean v0.11-based #252 implementation.
5. Confirm and implement the membership-based #189 policy.
6. Continue #328, #315, #103, and the KiCad 11 #257 transition as independent,
   focused series.
7. Carry #360 metadata through the catalog pipeline, reusing the v0.11
   Datasheet/Description contract rather than creating a second lookup path.

Keep [ROADMAP.md](https://github.com/mixelpixx/Konnect/blob/main/ROADMAP.md)
and Discussion #165 aligned with actual merged releases. A green or previously
tested PR is not a shipped capability until it lands and passes on the current
baseline.
