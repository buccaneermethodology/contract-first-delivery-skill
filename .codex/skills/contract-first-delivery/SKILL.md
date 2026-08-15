---
name: contract-first-delivery
description: Freeze implementation boundaries and create a testable contract package before coding. Use for new modules, schema-bearing outputs, AI-generated artifacts, compatibility-sensitive changes, manual golden oracles, or any task where implementation could outrun durable requirements.
---

# Contract First Delivery

Freeze the smallest durable contract that makes the next implementation slice bounded and testable.

## Workflow

1. Freeze goal, non-goals, users, system boundary, compatibility target, rollout, quality gates, test strategy, and change control in `constitution.json`.
2. Define inputs, outputs, dependencies, state changes, errors, constraints, validation, non-goals, and downstream consumers in `module-contract.json`.
3. Create `artifact.schema.json` before implementing structured output behavior.
4. Add `example.valid.json` and validate it against the schema.
5. For semantic or high-risk output, add a human-authored `golden.json` with source provenance and review notes. Never generate the oracle from the candidate it evaluates.
6. Separate blocking checks from advisory checks in `acceptance-policy.json` and state the evidence ceiling.
7. Run the packaged validator and resolve every blocking finding before coding.
8. Name the smallest safe implementation slice and keep it within the frozen contract.

Run the bundled example from the repository root:

```bash
python3 scripts/validate_contract_package.py examples/minimal-contract
```

Read [the complete reference](references/REFERENCE.md) when creating a package, interpreting finding codes, integrating the validator, or evolving a frozen contract.

## Decision Rule

If an implementation detail is unclear, harden the smallest missing contract surface first. Do not use code to discover goals, authority, compatibility, error semantics, or acceptance boundaries that should have been explicit inputs.

## Evidence Boundary

A passing validator proves only that the package has the required structure and explicit cross-file relationships checked by the script. It does not prove business semantics, production readiness, security, performance, or suitability for every project.
