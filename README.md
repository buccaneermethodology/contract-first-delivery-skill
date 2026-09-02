# Contract First Delivery Skill

`contract-first-delivery` helps teams freeze the full task or Session completion boundary before code is written, then deliver it through bounded implementation slices without silently narrowing the original scope. The repository includes an installable Codex Skill, a six-file minimal contract package, a standard-library validator, fail-closed tests, and a comprehensive reference.

## Install

Copy the Skill directory into your Codex skills directory:

```bash
cp -R .codex/skills/contract-first-delivery "${CODEX_HOME:-$HOME/.codex}/skills/contract-first-delivery"
```

Then invoke it as `$contract-first-delivery` when planning a new module or structured output.

## Quick start

```bash
python3 scripts/validate_contract_package.py examples/minimal-contract
python3 tests/run_tests.py
```

The validator exits `0` only when all blocking structural checks pass. This includes a complete must-have ledger, an ordered slice plan that covers it, and closeout fields that keep slice success separate from Session completion. Findings use stable `CFD-*` codes suitable for CI assertions.

## Repository layout

- `.codex/skills/contract-first-delivery/`: unique installable Skill source and full reference
- `examples/minimal-contract/`: constitution, module contract, schema, valid example, manual golden, and acceptance policy
- `scripts/validate_contract_package.py`: deterministic package validator
- `tests/run_tests.py`: positive and fail-closed regression cases
- `.github/workflows/validate.yml`: CI checks

See [the comprehensive reference](.codex/skills/contract-first-delivery/references/REFERENCE.md) for concepts, file contracts, workflow, finding codes, adoption, and compatibility guidance.

## Evidence boundary

Passing the bundled checks means the included package is structurally complete and internally consistent for the relationships the validator implements. It does not establish semantic truth, production readiness, security, or universal project maturity. Human review remains authoritative for goals, boundary decisions, and golden-oracle meaning.

## Version 2 migration

Version 2 intentionally makes completion discipline fail-closed. Existing v1 packages must add:

- `constitution.json.session_completion`, including the original must-have ledger, completion and continuation rules, allowed termination conditions, and Scope Delta policy;
- `module-contract.json.implementation_slices`, whose ordered entries collectively cover every original must-have;
- `acceptance-policy.json.required_closeout_fields`, separating `slice_verdict` from `session_terminal` and reporting remaining work.

The six filenames and existing finding codes remain stable. Missing or inconsistent completion surfaces now emit `CFD-MISSING-SESSION-COMPLETION` or `CFD-INCOMPLETE-SLICE-PLAN`.

## License

MIT. See [LICENSE](LICENSE).
