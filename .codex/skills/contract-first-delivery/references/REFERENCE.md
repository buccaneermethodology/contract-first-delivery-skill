# Contract First Delivery Reference

## 1. Purpose and fit

Contract-first delivery turns ambiguous implementation work into a bounded, reviewable package before code is written. It is useful when a module has structured inputs or outputs, compatibility obligations, meaningful error behavior, authority boundaries, high-cost rework, or model-generated artifacts whose shape alone cannot establish correctness.

Use it for:

- a new API, module, pipeline stage, or file format;
- generated JSON or another schema-bearing artifact;
- behavior with compatibility, rollout, approval, or write boundaries;
- semantic output that needs a human-authored oracle;
- changes where acceptance must distinguish blocking failures from advice.

Do not use it as a substitute for product discovery, security review, domain approval, performance measurement, or production operations. A small, reversible implementation with no durable interface may need only a lightweight inline contract rather than the complete example package.

## 2. Core concepts and authority

### Constitution

The constitution freezes decisions that implementation must not silently redefine: goal, non-goals, users, system boundary, compatibility target, rollout, quality gates, test strategy, and change control. It is the project-level boundary, not an implementation plan.

### Module contract

The module contract states purpose, inputs, outputs, dependencies, state changes, errors, validation, constraints, non-goals, and downstream consumers. It converts prose into observable behavior without choosing unnecessary internal details.

### Schema and example

The schema is the machine-readable shape contract. The valid example demonstrates one accepted instance and must pass the schema check. Schema validity does not prove that field values mean the right thing.

### Golden oracle

A golden captures a reviewed semantic expectation that schema alone cannot judge. Human or project authority owns its meaning. The candidate under evaluation must not generate its own golden; that would collapse evidence into self-certification.

### Acceptance policy

Blocking checks prevent implementation entry or acceptance. Advisory checks preserve useful observations without turning every improvement into a failure. Their identifiers must remain distinct and their evidence ceiling must be explicit.

### Non-collapsible boundaries

- A passing schema is not semantic approval.
- A generated candidate is not its own oracle.
- An implementation decision is not a goal or authority decision.
- An advisory observation is not automatically blocking.
- A validator report is evidence, not publication or production authority.

## 3. End-to-end workflow

1. Intake the request and identify the person or artifact authorized to define the goal.
2. Write the constitution and resolve ambiguity in goal, non-goals, boundary, compatibility, rollout, testing, and change control.
3. Write the module contract and make inputs, outputs, state changes, errors, validation, constraints, and consumers observable.
4. Define the output schema before implementing a producer.
5. Add a passing example grounded in representative input.
6. Add a manual golden when semantic meaning cannot be decided from shape alone. Record source identity, review status, decision notes, and that it was not candidate-generated.
7. Define blocking and advisory acceptance checks plus the maximum supported claim.
8. Run the validator. Treat any `CFD-*` finding other than `CFD-VALID` as blocking for the bundled package.
9. Name the smallest implementation slice that consumes the declared input and produces the declared output without widening authority.
10. Implement and test only that slice. If the contract changes, version and re-review the contract package before relying on new behavior.
11. At closeout, report what the evidence proves, what it does not prove, and what remains for later integration or operational validation.

## 4. Package and file contracts

The reference package contains exactly six JSON files:

```text
constitution.json
module-contract.json
artifact.schema.json
example.valid.json
golden.json
acceptance-policy.json
```

### `constitution.json`

Required keys:

- `goal`: one observable intended outcome;
- `non_goals`: exclusions that prevent accidental widening;
- `users`: people or systems served by the work;
- `system_boundary`: explicit inside/outside responsibilities;
- `compatibility_target`: supported runtime, data, or interface baseline;
- `technical_constraints`: constraints implementation must respect;
- `rollout_stages`: staged adoption sequence;
- `quality_gates`: checks required before progression;
- `test_strategy`: positive, negative, regression, or review surfaces;
- `change_control`: how contract changes are proposed and approved.

`target_workflows` is recommended but not required by the validator.

### `module-contract.json`

Required keys are `purpose`, `inputs`, `outputs`, `dependencies`, `state_changes`, `errors`, `validation_surface`, `constraints`, `non_goals`, and `downstream_consumers`. Consumers belong in the contract because seemingly local output changes can break external readers.

### `artifact.schema.json`

The bundled standard-library validator intentionally implements a small JSON Schema subset: `type`, `required`, `properties`, `items`, `enum`, and `additionalProperties: false`. Use a full JSON Schema implementation in projects that need formats, unions, numeric ranges, references, conditional schemas, or complete draft compliance. An unsupported or missing `type` fails closed.

### `example.valid.json`

This file is a concrete passing artifact. Keep it small enough to review and representative enough to exercise required fields and boundary-sensitive values.

### `golden.json`

Required trust signals are:

- `oracle_type` equals `manual`;
- `source_provenance.source_id` is non-empty;
- `source_provenance.manual_reviewed` is `true`;
- `source_provenance.generated_from_candidate` is `false`;
- `decision_notes` is non-empty;
- `artifact`, when present, satisfies the schema.

These fields make provenance explicit; they cannot prove the reviewer had the right authority or made the right semantic decision.

### `acceptance-policy.json`

`blocking_checks` must be a non-empty list, `advisory_checks` must be a list, each entry needs a unique `id` and a `rule`, and `claim_ceiling` must be non-empty. A project can add fields, but it should not allow a profile or formatter to downgrade a blocking result.

## 5. Running the example

From the repository root:

```bash
python3 scripts/validate_contract_package.py examples/minimal-contract
```

Expected result:

```text
CFD-VALID: contract package structure and declared relationships passed; semantic truth and production readiness are not established
```

Run the regression suite:

```bash
python3 tests/run_tests.py
```

The suite copies the positive fixture into temporary directories and introduces one bounded defect per case. It verifies that the validator exits nonzero and emits the expected stable finding code.

Compile the Python surfaces:

```bash
PYTHONPYCACHEPREFIX=/tmp/cfd-pycache python3 -m py_compile scripts/*.py tests/*.py
```

Validate the installable Skill with an installed `skill-creator`:

```bash
python3 /path/to/skill-creator/scripts/quick_validate.py .codex/skills/contract-first-delivery
```

CI also runs `tests/validate_skill_shape.py`, a dependency-free compatibility check. It protects the required package surfaces when the official tool is not installed, but it is not presented as the official validator.

## 6. Finding codes and failure behavior

| Code | Blocking meaning | Typical repair |
| --- | --- | --- |
| `CFD-PACKAGE-NOT-FOUND` | The supplied directory does not exist. | Pass the package directory explicitly. |
| `CFD-MISSING-CONSTITUTION` | The constitution is absent, unreadable, not an object, or lacks required boundaries. | Complete and review the constitution before coding. |
| `CFD-MISSING-CONTRACT` | The module contract is absent, unreadable, not an object, or incomplete. | Define observable module behavior and consumers. |
| `CFD-INVALID-SCHEMA` | The schema is absent, unreadable, or outside the supported structural subset. | Repair the schema or use a full validator for advanced keywords. |
| `CFD-EXAMPLE-SCHEMA-MISMATCH` | The example is absent, unreadable, or violates the schema. | Repair the example or review the schema intentionally. |
| `CFD-UNTRUSTED-GOLDEN` | The golden lacks manual provenance, comes from the candidate, lacks notes, or violates the schema. | Restore an independently reviewed, source-linked oracle. |
| `CFD-MISSING-ACCEPTANCE-POLICY` | The policy is absent, unreadable, collapses categories, duplicates IDs, or lacks a claim ceiling. | Separate blocking/advisory checks and state the evidence limit. |

The validator may emit more than one finding when defects are independent. Output ordering is deterministic: required file order first, followed by cross-file checks.

## 7. Positive, negative, blocking, and advisory checks

The positive example proves that the packaged fixture can traverse the implemented structural path. Negative tests prove that named malformed shapes fail closed. Neither result proves all malformed shapes are covered.

The bundled package treats missing boundaries, invalid schema relationships, untrusted golden provenance, and malformed acceptance policy as blocking. Wording improvements are advisory because they do not change the declared structural contract. A project may add stricter checks, but it should document changes and avoid silently reclassifying existing blocking findings.

Common mistakes include:

- starting implementation with a goal but no non-goals;
- treating a schema as the entire module contract;
- using a generated output as the golden because it “looks right”;
- listing checks without saying which ones block;
- changing a schema without updating example, golden, and consumers;
- reporting `CFD-VALID` as business approval or production readiness.

## 8. Progressive adoption and integration

Adopt the method in small steps:

1. Start with constitution and module contract for one risky slice.
2. Add schema and a valid example when the output is structured.
3. Add a golden only where semantic review adds material value.
4. Add acceptance policy and the validator to local development.
5. Add the tests and validator to CI after the contract stabilizes.
6. Version contract changes and notify downstream consumers.

For an existing codebase, document current behavior as a compatibility baseline before proposing a target contract. Mark mismatches as observed legacy behavior, intended migration, or unresolved decision. Do not rewrite history by describing target behavior as already implemented.

The validator accepts an explicit directory and uses only the Python standard library, so it can run from any working directory. Integrations should consume its process exit status and stable finding codes rather than parsing human wording.

## 9. Provenance and evidence ceiling

The method is generalized from bounded project practice and representative positive/negative validation. The public fixture is deliberately generic and self-contained. No private project artifact, user data, secret, or environment-specific absolute path is needed to run it.

The strongest supported claim after all bundled checks pass is:

> The supplied fixture is structurally complete and satisfies the explicit relationships implemented by this validator.

It does not support claims that the package is semantically correct for a particular business, secure, performant, production-ready, approved, published, or mature across arbitrary projects. Those claims need independent evidence and the appropriate human or operational authority.

## 10. Maintenance, extension, and compatibility

Treat the six filenames, stable finding codes, and process exit behavior as the v1 compatibility surface. Additive fields are safe when older consumers ignore them. Renaming files, changing code meanings, weakening a blocking check, or expanding the supported schema dialect requires a documented version decision and updated examples/tests.

When extending the validator:

- add one positive or negative fixture for each new behavior;
- keep errors deterministic and source-local;
- preserve blocking/advisory separation;
- document unsupported schema features instead of partially accepting them;
- update the reference and CI in the same change;
- avoid external dependencies unless their installation and version policy are explicit.

When evolving a golden, preserve the previous oracle or its review record so a later candidate cannot erase evidence of earlier failures. When evolving the constitution or module contract, record why the boundary changed and which consumers must revalidate.
