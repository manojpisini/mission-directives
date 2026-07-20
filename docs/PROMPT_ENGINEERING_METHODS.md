# Prompt Engineering Methods

The suite uses task-fit methods rather than adding every technique to every prompt.

## Core methods

- **Explicit task contract:** identity, observable outcome, inputs, constraints, outputs, and completion criteria.
- **Semantic delimitation:** XML-style tags distinguish instructions, context, examples, untrusted data, and output requirements.
- **Prompt chaining:** complex work is decomposed into evidence, brief, production, review, and verification stages when the stages have distinct responsibilities.
- **Retrieval and grounding:** factual work retrieves current or authoritative evidence and maps claims to sources.
- **Few-shot examples:** examples are used only when they materially clarify style, classification, transformation, or output shape; counterexamples define prohibited output when useful.
- **Structured outputs:** machine-consumed artifacts use schemas; human artifacts use explicit headings, tables, IDs, and acceptance criteria.
- **Tool and skill routing:** tools are selected by task and output contract, with least privilege and explicit verification.
- **Multiple-candidate exploration:** creative and strategic work generates genuinely different directions before convergence when the decision benefits from comparison.
- **Challenge and counterevidence:** high-stakes analysis searches for contradictions, alternative explanations, and failure cases.
- **Self-consistency without hidden-rationale dependence:** independent candidate solutions or checks may be compared, but final artifacts record evidence and concise rationale rather than private reasoning traces.
- **Rubric-guided revision:** outputs are revised against task-specific quality gates instead of vague requests to “improve.”
- **Multimodal planning:** visual tasks specify audience, medium, dimensions, information hierarchy, interaction, accessibility, and export before production.

## Efficiency rules

1. Put stable control contracts in shared prompts, not every capability body.
2. Include only context that changes the result.
3. Prefer precise nouns, verbs, criteria, and examples over repeated emphasis.
4. Ask for the smallest sufficient artifact and then compose larger workflows through scenarios.
5. Do not request hidden chain-of-thought; request evidence, calculations, assumptions, decisions, and concise rationale.
6. Treat long context as searchable evidence, not as a requirement to restate everything.
7. Verify outputs with deterministic checks whenever possible.

## Anti-slop standard

Outputs must avoid generic openings, inflated claims, repetitive summaries, fake quotations, invented metrics, keyword stuffing, ornamental jargon, empty transitions, symmetrical filler, and conclusions that merely repeat the introduction. Specificity, evidence, voice, structure, and useful decisions take priority over length.

## Proof-oriented prompt refinement

Optimization is accepted only when representative fixtures show equal or better correctness, safety, clarity, artifact quality, and efficiency. Token reduction that weakens evidence, authorization, uncertainty, verification, or stop behavior is a regression. Pairing, examples, tags, and tool use are evaluated as hypotheses rather than assumed improvements.

## Adding a distinct prompt capability

Run `MD-199` for semantic overlap analysis and metadata refinement, then use the deterministic addition tool for registration. The approved dry-run proposal must name the next ID, canonical filename, capability ID, category, role, modes, risk, references, templates, skills, and department packs. Promotion is transactional and succeeds only after the staged suite regenerates and validates every affected catalog, graph, fixture, crosswalk, test, receipt, and manifest.
