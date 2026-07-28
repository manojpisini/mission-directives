# Documentation Library

The documentation library explains how to operate, author, validate, secure, and extend the prompt suite. It is organized by reader task rather than file age or generation order.

## Essential reading path

1. [Getting Started](GETTING_STARTED.md)
2. [Installation and Project Integration Guide](INSTALLATION_AND_PROJECT_INTEGRATION_GUIDE.md)
3. [User Manual](USER_MANUAL.md)
4. [Operator Guide](OPERATOR_GUIDE.md)
5. [Architecture Guide](ARCHITECTURE_GUIDE.md)
6. [Prompt Body Authoring Guide](PROMPT_BODY_AUTHORING_GUIDE.md)
7. [Evaluation Manual](EVALUATION_MANUAL.md)
8. [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md)
9. [Router Keyword Catalog and Scoring Guide](ROUTER_KEYWORD_CATALOG_AND_SCORING_GUIDE.md)
10. [Installed Runtime Payload Guide](INSTALLED_RUNTIME_PAYLOAD_GUIDE.md)
11. [GitHub Actions Failure History and Pre-Push Guide](GITHUB_ACTIONS_FAILURE_HISTORY_AND_PRE_PUSH_GUIDE.md)

Repository contributors should also read the root [Contributing Guide](../CONTRIBUTING.md).

Install persistently with `uv tool install mission-directives`, `pipx install mission-directives`, or `python -m pip install --user mission-directives`. Use `uvx mission-directives <command>` for one-off execution or `python -m mission_directives <command>` after pip installation.

## Prompt-body integrity manuals

The prompt-body contract is a first-class subsystem. These manuals define it in detail:

- [Prompt Body Authoring Guide](PROMPT_BODY_AUTHORING_GUIDE.md)
- [Completion Criteria Guide](COMPLETION_CRITERIA_GUIDE.md)
- [Tool Policy and Authorization Guide](TOOL_POLICY_AND_AUTHORIZATION_GUIDE.md)
- [Runtime Marker Protocol](RUNTIME_MARKER_PROTOCOL.md)
- [Pair Authoring and Verification Guide](PAIR_AUTHORING_AND_VERIFICATION_GUIDE.md)
- [Executive Decision Rules Guide](EXECUTIVE_DECISION_RULES_GUIDE.md)
- [Prompt Body Validation Guide](PROMPT_BODY_VALIDATION_GUIDE.md)

## Proof and runtime manuals

- [Evaluation Manual](EVALUATION_MANUAL.md)
- [CI and Testing Guide](CI_AND_TESTING_GUIDE.md)
- [Model Routing Guide](MODEL_ROUTING_GUIDE.md)
- [Skill Supply-Chain Guide](SKILL_SUPPLY_CHAIN_GUIDE.md)
- [Telemetry and Observability Guide](TELEMETRY_AND_OBSERVABILITY_GUIDE.md)
- [Installed Runtime Payload Guide](INSTALLED_RUNTIME_PAYLOAD_GUIDE.md)
- [Documentation Site Guide](DOCUMENTATION_SITE_GUIDE.md)
- [Recovery and Rollback Guide](RECOVERY_AND_ROLLBACK_GUIDE.md)

## Governance and integration

- [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md)
- [Router Keyword Catalog and Scoring Guide](ROUTER_KEYWORD_CATALOG_AND_SCORING_GUIDE.md)
- [Compatibility and Identity Guide](COMPATIBILITY_AND_IDENTITY_GUIDE.md)
- [Agent Library Integration Guide](AGENT_LIBRARY_INTEGRATION_GUIDE.md)
- [Scenario Authoring Guide](SCENARIO_AUTHORING_GUIDE.md)
- [Contributor Guide](CONTRIBUTOR_GUIDE.md)
- [GitHub Actions Failure History and Pre-Push Guide](GITHUB_ACTIONS_FAILURE_HISTORY_AND_PRE_PUSH_GUIDE.md)
- [Security Operations Guide](SECURITY_OPERATIONS_GUIDE.md)
- [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- [Manual Quality Standard](MANUAL_QUALITY_STANDARD.md)

## Rebuilding and verifying the documentation surface

Documentation references are checked by the suite validator. Prompt-body statistics are generated from the prompt files, not manually maintained:

```bash
python tools/audit_prompt_bodies.py
python tools/audit_prompt_bodies.py --check
python tools/validate_suite.py
```

`BODY_QUALITY_AUDIT.json` is machine-readable. `BODY_QUALITY_AUDIT.md` is the human summary.
## Documentation website

The static Astro site is published at <https://manojpisini.github.io/mission-directives/>. Its top-level [Getting Started](https://manojpisini.github.io/mission-directives/getting-started.html), [Installation](https://manojpisini.github.io/mission-directives/installation.html), and [Contributing](https://manojpisini.github.io/mission-directives/contributing.html) pages reuse canonical repository Markdown. See the [Documentation Site Guide](DOCUMENTATION_SITE_GUIDE.md).
