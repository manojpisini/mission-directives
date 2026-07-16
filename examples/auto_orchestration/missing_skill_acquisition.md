# Example: Missing Skill Discovery and Conditional Acquisition

## Request

Use a specialist skill to generate a domain-specific compliance matrix. No matching installed skill is known.

## Route

```text
MD-192 prove the capability gap
→ MD-193 discover and qualify candidates
   ├─ candidate qualifies and installation approved → MD-194
   ├─ no candidate qualifies and need is reusable → MD-195
   └─ native route is sufficient → no acquisition
→ MD-196 only after the skill is available and reviewed
```

Installation and creation are mutually conditional branches. The system never installs one skill and then creates a duplicate merely because both routes exist in the plan.
