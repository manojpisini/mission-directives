# Skill Routing

Skills are optional execution adapters, not hidden prompt powers. The router probes availability, trust, and fit before selection; unavailable skills never block the native prompt path.

## Selection rules

1. Match the requested artifact and acceptance criteria, not merely keywords.
2. Choose one primary production skill and only the supporting skills required for review, brand, export, or accessibility.
3. Do not invoke a design skill before the content, data, or narrative brief is sufficiently stable.
4. Preserve the prompt output contract even when a skill is used.
5. Record the selected skill, reason, inputs, outputs, limitations, and verification evidence.
6. Treat skill-generated code, diagrams, and assets as untrusted until reviewed and validated.

## Preferred skill matrix

| Skill | Primary use | Typical supporting role |
|---|---|---|
| `blueprinter` | Create structured blueprints, architecture sheets, process maps, and implementation-ready visual specifications. | blueprints, system maps, process architecture, implementation plans |
| `brand-guidelines` | Apply or produce brand systems, visual identity rules, typography, color, assets, voice, and cross-channel consistency. | brand guidelines, branded decks, campaign systems, asset governance |
| `dashboard-builder` | Build analytical dashboards and operational decision surfaces from structured data and user questions. | KPI dashboards, operational views, interactive analytics, monitoring surfaces |
| `canvas-design` | Compose polished static visual layouts, posters, cards, infographics, moodboards, and presentation graphics. | visual compositions, infographics, moodboards, campaign assets |
| `frontend-slides` | Produce browser-native presentation decks with HTML, CSS, JavaScript, responsive layout, and controlled motion. | HTML slide decks, interactive presentations, speaker-led demos |
| `excalidraw-diagram-generator` | Create editable Excalidraw-style diagrams for collaborative workshops, architecture, flows, and ideation. | whiteboards, workshop diagrams, editable flows, rough-to-clear systems maps |
| `design-taste-frontend-v1` | Improve frontend composition, visual taste, interaction detail, hierarchy, and distinctive product polish. | frontend redesign, landing pages, interactive artifacts, dashboard polish |
| `html-svg-diagrams` | Create semantic, scalable, accessible diagrams and infographics using HTML and SVG. | SVG diagrams, technical schematics, data graphics, embeddable visuals |
| `html-ppt` | Translate structured slide content and visual systems into presentation-compatible output while preserving layout intent. | presentation export, deck packaging, slide conversion |
| `impeccable` | Perform final visual and interaction quality review, eliminating rough edges, inconsistency, and presentation defects. | final polish, visual QA, presentation QA, frontend QA |
| `stop-slop` | Remove generic, inflated, repetitive, clichéd, unsupported, or machine-like writing while preserving meaning and voice. | scripts, papers, blogs, pitches, reports, creative editing |
| `visual-assets` | Build deliberate editable visual assets from SVG, CSS, HTML, and vanilla JavaScript. | illustrations, infographics, vector graphics, report exhibits, presentation assets, animated explainers |
| `strudel` | Create and refine Strudel music code and reproducible live-coding arrangements. | music patterns, composition systems, timed audiovisual support |
| `web-artifacts-builder` | Build self-contained interactive web artifacts, microsites, prototypes, explainers, and data experiences. | interactive artifacts, microsites, prototypes, web explainers |

## Common compositions

| Outcome | Primary | Supporting |
|---|---|---|
| Browser-native slide deck | `frontend-slides` | `brand-guidelines`, `impeccable`, optionally `html-ppt` |
| Analytical dashboard | `dashboard-builder` | `design-taste-frontend-v1`, `impeccable` |
| Technical blueprint | `blueprinter` | `html-svg-diagrams`, optionally `excalidraw-diagram-generator` |
| Branded infographic or editorial illustration | `visual-assets` or `canvas-design` | `brand-guidelines`, `impeccable` |
| Collaborative workshop map | `excalidraw-diagram-generator` | `blueprinter` |
| Interactive explainer or prototype | `web-artifacts-builder` | `design-taste-frontend-v1`, `impeccable` |
| Research-backed script or paper | native research and writing prompts | `stop-slop` for final editing |

Named skills are aliases supplied by the operator or runtime. Their actual schemas remain authoritative when loaded.

## Supply-chain enforcement

Every installable skill has a `skills.lock.json` entry. A usable production lock contains the exact repository commit and tarball SHA-256. Unresolved or review-required locks block automatic installation and automatic selection.

Trust and maturity are distinct:

- `trust_tier` records provenance and review evidence;
- `maturity` records operational promotion;
- `lock_status` records byte-level pinning;
- `live_status` in the conformance fixture records observed behavior.

A skill is auto-selectable only when all applicable controls pass. Skill-generated output remains quarantined until independent routed verification.


## Conditional acquisition and generic execution

`MD-192` determines whether a skill is genuinely required. `MD-193` discovers candidates, `MD-194` installs an approved exact skill into both global locations, `MD-195` creates a skill only as a last resort, and `MD-196` executes any exact installed skill through typed placeholders. `MD-197` may loop that execution only when the loop eligibility contract passes.

## Installed but unmapped skills

The supplied OpenCode inventory may contain skills that are not yet curated in `skill_registry.json`. An explicit request for such a skill routes through `MD-192` and may reach `MD-196` only after probing its `SKILL.md`, permissions, provenance, input/output contract, side effects, and task fit. Presence on disk is evidence of availability, not trust or automatic authority. Missing skills instead route through `MD-193` and the governed acquisition branch.

## Installed inventory coverage

The supplied OpenCode inventory is fully represented in `skill_registry.json`. Registration makes a skill inspectable; it does not make it trusted or automatically selectable. Personal skills `visual-assets` and `strudel` are approved local capabilities, while other detected local skills default to experimental runtime probing. Model image-generation skills remain explicitly excluded.

## Generic adapter rule

Any exact installed skill may be routed through `MD-196` only after `MD-192` proves genuine task fit. The adapter is not limited to visual or design work. Any repeated execution must separately pass `MD-197` loop eligibility and `MD-198` exit adjudication.

## Skills referenced by imported prompts

Prompt addition validates every preferred skill against `skill_registry.json` and updates that skill's prompt routes. This is routing metadata only: the workflow does not install, approve, execute, or trust a skill. Unknown skills fail closed and must use the existing discovery, lock, review, conformance, and registration workflow before they can be referenced.
