# Documentation Library

The documentation library explains how to operate, author, validate, secure, and extend the prompt suite. It is organized by reader task rather than file age or generation order.

## Essential reading path

1. [User Manual](USER_MANUAL.md)
2. [Operator Guide](OPERATOR_GUIDE.md)
3. [Architecture Guide](ARCHITECTURE_GUIDE.md)
4. [Prompt Body Authoring Guide](PROMPT_BODY_AUTHORING_GUIDE.md)
5. [Evaluation Manual](EVALUATION_MANUAL.md)
6. [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md)

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
- [Recovery and Rollback Guide](RECOVERY_AND_ROLLBACK_GUIDE.md)

## Governance and integration

- [Root Agent Guidance and Keyword Routing Guide](ROOT_AGENT_GUIDANCE_AND_KEYWORD_ROUTING_GUIDE.md)
- [Compatibility and Identity Guide](COMPATIBILITY_AND_IDENTITY_GUIDE.md)
- [Agent Library Integration Guide](AGENT_LIBRARY_INTEGRATION_GUIDE.md)
- [Scenario Authoring Guide](SCENARIO_AUTHORING_GUIDE.md)
- [Contributor Guide](CONTRIBUTOR_GUIDE.md)
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
