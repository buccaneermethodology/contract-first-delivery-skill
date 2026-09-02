---
name: contract-first-delivery
description: Freeze full task or Session completion boundaries and create a testable contract package before coding. Use for new modules, schema-bearing outputs, AI-generated artifacts, compatibility-sensitive changes, manual golden oracles, multi-slice delivery, or any task where implementation could outrun or silently narrow durable requirements.
---

# Contract First Delivery

Freeze the full completion boundary, then identify the smallest safe first implementation slice without narrowing the original task or Session.

## Workflow

1. Preserve the original goal and all must-haves. Freeze non-goals, users, system boundary, compatibility target, rollout, quality gates, test strategy, change control, the full completion rule, allowed termination conditions, and Scope Delta policy in `constitution.json`.
2. Define inputs, outputs, dependencies, state changes, errors, constraints, validation, non-goals, and downstream consumers in `module-contract.json`.
3. Create `artifact.schema.json` before implementing structured output behavior.
4. Add `example.valid.json` and validate it against the schema.
5. For semantic or high-risk output, add a human-authored `golden.json` with source provenance and review notes. Never generate the oracle from the candidate it evaluates.
6. Separate blocking checks from advisory checks in `acceptance-policy.json` and state the evidence ceiling.
7. Run the packaged validator and resolve every blocking finding before coding.
8. Map an ordered implementation-slice plan to every original must-have. Name the smallest safe first slice and keep every slice within the frozen contract.
9. After each slice, re-evaluate the original must-have ledger. Continue to the next ready slice while the completion rule is unsatisfied and no human decision or verified blocker prevents progress.
10. At closeout, report the slice verdict separately from the Session verdict, remaining must-haves, Scope Delta, next slice, and whether a human decision is required.

## Completion Discipline

The smallest safe implementation slice is an entry point, not a default task or Session completion boundary.

- Do not replace the original scope with a smaller contract created for the first slice.
- Do not mark the task or Session done because one schema, fixture, contract test, implementation slice, or validation gate passed.
- Treat deletion, weakening, deferral, or transfer of an original must-have as a Scope Delta. Require explicit human approval for a material Scope Delta before using it to declare completion.
- Stop before full completion only for an allowed termination condition. Distinguish a verified blocker or required human decision from ordinary unfinished work.
- Final validation must compare landed artifacts with both the slice contract and the original goal, must-have ledger, and completion rule.

Run the bundled example from the repository root:

```bash
python3 scripts/validate_contract_package.py examples/minimal-contract
```

Read [the complete reference](references/REFERENCE.md) when creating a package, interpreting finding codes, integrating the validator, or evolving a frozen contract.

## Decision Rule

If an implementation detail is unclear, harden the smallest missing contract surface first. Do not use code to discover goals, authority, compatibility, error semantics, or acceptance boundaries that should have been explicit inputs. Hardening a smaller surface must not redefine the original completion boundary.

## Evidence Boundary

A passing validator proves only that the package has the required structure and explicit cross-file relationships checked by the script. It does not prove business semantics, production readiness, security, performance, or suitability for every project.
