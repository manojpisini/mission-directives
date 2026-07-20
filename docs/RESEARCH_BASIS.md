# Research Basis

The suite applies prompt-engineering techniques selectively according to task, model, risk, and output medium. No technique is treated as a universal incantation. The operating standard is clarity, relevant context, explicit boundaries, fit-for-purpose examples, structured outputs, tool-aware verification, and empirical evaluation.

## Primary guidance

- [OpenAI prompt engineering guide](https://developers.openai.com/api/docs/guides/prompt-engineering): clear instruction hierarchy, Markdown and XML boundaries, examples, relevant context, retrieval, and evaluation-aware iteration.
- [Anthropic prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview): clarity, examples, XML structuring, role prompting, reasoning, and prompt chaining as task-fit techniques.
- [Google prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies): clear and specific instructions, context, examples, decomposition, and iterative refinement.

## Research surveys

- [The Prompt Report](https://arxiv.org/abs/2406.06608): a broad taxonomy of language-model and multimodal prompting techniques, used here to avoid treating one method as sufficient for every task.
- [A Systematic Survey of Prompt Engineering in Large Language Models](https://arxiv.org/abs/2402.07927): application-oriented coverage of prompting methods, strengths, limitations, models, and datasets.

## Operator-supplied explorations

- [Use of signs in prompts](https://medium.com/@Lidinwise/hidden-gems-of-prompt-engineer-the-use-of-signs-8df93ac03dbb): informed the readable placeholder and artifact-reference notation.
- [XML-style tags for prompt structure](https://medium.com/@TechforHumans/effective-prompt-engineering-mastering-xml-tags-for-clarity-precision-and-security-in-llms-992cae203fdc): informed consistent semantic delimiters and the warning against excessive nesting.
- [Community discussion of prompt meta tags](https://www.reddit.com/r/ChatGPTPro/comments/1ehx9zi/exploring_meta_tags_for_ai_prompts/): treated as exploratory practitioner experience, not as evidence that unofficial tags have privileged model behavior.

## Applied conclusions

1. Tags and signs are readability and delimitation mechanisms; they are not hidden commands or standalone security controls.
2. Stable contracts belong in the control plane; capability prompts contain only task-changing evidence, method, risk, medium, and quality details.
3. Examples are optional and should be diverse, relevant, and short enough to clarify rather than dominate.
4. Factual work requires retrieval, provenance, claim support, uncertainty, and verification.
5. Creative work benefits from divergent candidates and rubric-guided convergence, but imaginative work must not manufacture evidence.
6. Complex work should be chained only when stages have genuinely different responsibilities and a useful handoff.
7. Visual and interactive outputs need medium-specific contracts, accessibility, responsive behavior, and exact export review.
8. Prompt quality is an empirical property: representative fixtures, adversarial cases, and regression evaluation matter more than ornamental complexity.

## Evidence standard for suite claims

Guidance and surveys justify methods to test, not claims that this specific suite performs well. Suite-level quality claims require its own fixtures, model runs, skill conformance, and human review. The package therefore separates structural validation from external behavioral evidence and records unmeasured surfaces explicitly.
