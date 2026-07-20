# Security Testing and Simulation Boundaries

Security prompts are defensive capabilities for systems the operator owns or is explicitly authorized to test.

## Required authorization

Attack simulation, exploit reproduction, model red teaming, credential rotation, production changes, permission changes, and incident containment require an approval receipt containing target, exclusions, environment, identities, data, methods, rate limits, time window, approver, contacts, recovery plan, and expiration.

## Prohibited behavior

The suite does not authorize targeting third parties, uncontrolled internet scanning, stealth, persistence, destructive payloads, ransomware behavior, credential theft, evasion of monitoring, data exfiltration, denial of service against real users, or publication of reusable weaponized artifacts.

## Safe escalation ladder

1. threat model and tabletop analysis;
2. passive configuration and code review;
3. static and dependency analysis;
4. benign unit and integration abuse cases;
5. sandboxed reproduction with synthetic data;
6. controlled staging validation with monitoring;
7. production validation only when explicitly authorized and safer evidence is insufficient.

Use the lowest rung that can answer the question. Stop immediately when observed impact exceeds the approval boundary.
