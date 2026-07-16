# Visual Assets Integration Guide

## Purpose

`visual-assets` is a user-owned local skill for deliberate, editorially designed visual construction. It builds assets from primitives:

- SVG paths and shapes;
- CSS;
- semantic HTML;
- vanilla JavaScript;
- optional controlled animation.

It is intended to produce the kind of visual found in a carefully edited magazine, annual report, research paper, technical publication, or high-quality presentation—an artifact with a clear communication purpose and visible design decisions.

It is **not** a model image-generation route. It should not substitute screenshots, stock icon packs, raster clip art, or a chart library's untouched default theme for design work.

## Appropriate outputs

- infographics and data stories;
- editorial illustrations;
- technical-paper figures;
- conceptual diagrams;
- architecture and process visuals;
- maps and relationship diagrams when the data supports them;
- report exhibits;
- presentation hero assets and supporting figures;
- vector icon or symbol systems;
- campaign and brand mock assets;
- accessible animated explainers;
- HTML/SVG interactive visuals;
- reusable visual primitives.

## When not to use it

Do not invoke `visual-assets` when:

- plain text or a simple table communicates the information better;
- an existing approved asset already satisfies the need;
- the visual brief, data, or factual spine is not stable;
- the task requires photorealistic or model-generated imagery;
- the output cannot be verified for accuracy or accessibility;
- a visual would be decorative and add no information, explanation, emotion, or brand value;
- the expected design gain does not justify the cost.

## Required brief

Before execution, freeze:

```yaml
communication_job:
audience:
placement:
source_facts_or_data:
primary_message:
secondary_details:
visual_form:
dimensions_and_crop_rules:
brand_tokens:
typography:
interaction_or_motion:
accessibility_alternative:
editability_requirements:
export_formats:
prohibited_elements:
acceptance_rubric:
```

The skill must not invent data, claims, brand rules, or source relationships to make a composition more convenient.

## Routed prompt areas

The suite routes `visual-assets` to relevant capabilities including:

- editorial research and publication packages;
- academic papers and technical figures;
- scripts and storyboards;
- moodboards and concept development;
- brand identity and campaigns;
- presentations and browser-native slides;
- dashboards, infographics, diagrams, and interactive artifacts;
- event and learning materials;
- social content;
- media production;
- professional documents, portfolios, executive reports, and report production.

`MD-192` still decides whether the skill is genuinely useful for each task. Preferred routing is not mandatory invocation.

## Presentation integration

For a deck:

1. `MD-101` freezes narrative and slide purpose.
2. Identify slides that require a real visual communication asset.
3. `MD-196` invokes `visual-assets` with one asset brief at a time or a finite queue.
4. The deck producer places the verified source asset without flattening it unnecessarily.
5. `MD-109` checks hierarchy, contrast, text alternatives, responsive behavior, and exact export.

A slide should not receive an illustration merely to fill empty space. Every asset must support the slide's job.

## Infographic and technical-figure integration

For factual visuals:

- bind every number, category, relationship, and label to `@EVIDENCE:{id}`;
- distinguish measured values from estimates and illustrative geometry;
- choose a form that does not exaggerate magnitude or certainty;
- retain an accessible text or table alternative;
- verify units, scales, ordering, legends, and annotations;
- keep source files editable.

For conceptual illustrations, label metaphor and interpretation rather than presenting them as measured diagrams.

## Animation

Animation is acceptable when it explains sequence, transition, causality, comparison, or focus. It must:

- have a reduced-motion path;
- preserve meaning when paused or exported statically;
- avoid gratuitous looping;
- avoid seizure-risk timing and flashes;
- keep controls keyboard accessible when interactive;
- remain performant in the intended medium.

## Batch production

Use `MD-197` only for a genuine finite queue. Each asset receives its own communication job and rubric. Shared tokens and primitives are encouraged; cloned composition without regard to meaning is not.

Outer loop:

```text
brief item → execute visual-assets → quarantine → verify → accept/residualize → next item
```

Optional inner loop:

```text
failed measurable criterion → targeted refinement hypothesis → new asset → independent review → exit decision
```

## Quality gates

A visual asset passes only when applicable checks succeed:

### Information

- factual values and relations match sources;
- the intended insight is understandable;
- hierarchy reflects importance;
- visual encoding does not mislead;
- labels, legends, and annotations are complete.

### Editorial design

- composition has a deliberate point of view;
- typography, spacing, and rhythm are controlled;
- the asset is not a generic template default;
- detail supports rather than obscures the message;
- variants remain coherent without becoming identical.

### Technical

- valid SVG/HTML/CSS/JS;
- no unexpected network dependencies;
- responsive or dimension-correct behavior;
- editable primitives;
- no clipping, overflow, broken fonts, or hidden labels;
- deterministic export where required.

### Accessibility

- sufficient contrast;
- readable labels at final size;
- semantic structure where interactive;
- keyboard operation;
- text alternative or data table;
- reduced-motion support.

### Brand and rights

- approved tokens and voice;
- no unlicensed stock assets or copied icon systems;
- source and ownership recorded;
- no misleading imitation of another brand or publication.

## Verification and quarantine

Raw output remains quarantined until the target prompt's verification contract or `MD-109` passes. The receipt records:

- skill ID and alias resolution;
- brief and input hashes;
- exact source files;
- output paths;
- validation results;
- accessibility review;
- export results;
- unresolved issues;
- lineage into reports, slides, sites, or publications.
