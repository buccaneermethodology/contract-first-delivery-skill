#!/usr/bin/env python3
"""Validate the contract-first-delivery six-file example package."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple


Finding = Tuple[str, str]

FILES = {
    "constitution": ("constitution.json", "CFD-MISSING-CONSTITUTION"),
    "contract": ("module-contract.json", "CFD-MISSING-CONTRACT"),
    "schema": ("artifact.schema.json", "CFD-INVALID-SCHEMA"),
    "example": ("example.valid.json", "CFD-EXAMPLE-SCHEMA-MISMATCH"),
    "golden": ("golden.json", "CFD-UNTRUSTED-GOLDEN"),
    "acceptance": ("acceptance-policy.json", "CFD-MISSING-ACCEPTANCE-POLICY"),
}

CONSTITUTION_KEYS = {
    "goal",
    "non_goals",
    "users",
    "system_boundary",
    "compatibility_target",
    "technical_constraints",
    "rollout_stages",
    "quality_gates",
    "test_strategy",
    "session_completion",
    "change_control",
}
CONTRACT_KEYS = {
    "purpose",
    "inputs",
    "outputs",
    "dependencies",
    "state_changes",
    "errors",
    "validation_surface",
    "constraints",
    "non_goals",
    "downstream_consumers",
    "implementation_slices",
}
COMPLETION_KEYS = {
    "must_haves",
    "completion_rule",
    "continuation_rule",
    "allowed_termination_conditions",
    "scope_delta_policy",
}
REQUIRED_CLOSEOUT_FIELDS = {
    "slice_verdict",
    "session_terminal",
    "remaining_must_haves",
    "scope_delta",
    "next_slice",
    "human_decision_required",
}


def load_json(path: Path, code: str, findings: List[Finding]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        findings.append((code, f"{path.name} is not readable JSON: {exc}"))
        return None


def require_object_keys(
    value: Any, required: Iterable[str], code: str, label: str, findings: List[Finding]
) -> None:
    if not isinstance(value, dict):
        findings.append((code, f"{label} must be a JSON object"))
        return
    missing = sorted(set(required) - set(value))
    if missing:
        findings.append((code, f"{label} is missing keys: {', '.join(missing)}"))


def matches_type(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return False


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_completion_plan(
    constitution: Any, contract: Any, findings: List[Finding]
) -> None:
    completion = (
        constitution.get("session_completion") if isinstance(constitution, dict) else None
    )
    completion_valid = isinstance(completion, dict) and COMPLETION_KEYS <= set(completion)
    must_have_ids: List[str] = []
    if completion_valid:
        must_haves = completion.get("must_haves")
        completion_valid = isinstance(must_haves, list) and bool(must_haves)
        if completion_valid:
            completion_valid = all(
                isinstance(item, dict)
                and is_non_empty_string(item.get("id"))
                and is_non_empty_string(item.get("requirement"))
                and is_non_empty_string(item.get("acceptance"))
                for item in must_haves
            )
            if completion_valid:
                must_have_ids = [item["id"] for item in must_haves]
                completion_valid = len(must_have_ids) == len(set(must_have_ids))
        termination = completion.get("allowed_termination_conditions")
        completion_valid = (
            completion_valid
            and is_non_empty_string(completion.get("completion_rule"))
            and is_non_empty_string(completion.get("continuation_rule"))
            and isinstance(termination, list)
            and bool(termination)
            and all(is_non_empty_string(item) for item in termination)
            and is_non_empty_string(completion.get("scope_delta_policy"))
        )
    if not completion_valid:
        findings.append(
            (
                "CFD-MISSING-SESSION-COMPLETION",
                "session completion must preserve unique must-haves with acceptance evidence, completion and continuation rules, allowed termination conditions, and Scope Delta policy",
            )
        )

    slices = contract.get("implementation_slices") if isinstance(contract, dict) else None
    slices_valid = isinstance(slices, list) and bool(slices)
    slice_ids: List[str] = []
    covered: List[str] = []
    if slices_valid:
        known_ids: set[str] = set()
        for index, item in enumerate(slices):
            item_valid = (
                isinstance(item, dict)
                and is_non_empty_string(item.get("id"))
                and isinstance(item.get("covers"), list)
                and bool(item.get("covers"))
                and all(is_non_empty_string(value) for value in item.get("covers", []))
                and isinstance(item.get("depends_on"), list)
                and all(is_non_empty_string(value) for value in item.get("depends_on", []))
                and item.get("readiness") in {"ready", "ready_after_dependencies", "blocked"}
                and is_non_empty_string(item.get("outcome"))
            )
            if not item_valid:
                slices_valid = False
                continue
            slice_id = item["id"]
            dependencies = item["depends_on"]
            if slice_id in known_ids or slice_id in dependencies:
                slices_valid = False
            if any(dependency not in known_ids for dependency in dependencies):
                slices_valid = False
            if index == 0 and item["readiness"] != "ready":
                slices_valid = False
            known_ids.add(slice_id)
            slice_ids.append(slice_id)
            covered.extend(item["covers"])
        if completion_valid and (
            set(covered) != set(must_have_ids)
            or any(item not in set(must_have_ids) for item in covered)
        ):
            slices_valid = False
    if not slices_valid or len(slice_ids) != len(set(slice_ids)):
        findings.append(
            (
                "CFD-INCOMPLETE-SLICE-PLAN",
                "ordered implementation slices must be valid, depend only on earlier slices, and collectively cover every original must-have without unknown references",
            )
        )


def validate_instance(instance: Any, schema: Any, location: str = "$") -> List[str]:
    """Validate the intentionally supported JSON Schema subset used by the fixture."""
    errors: List[str] = []
    if not isinstance(schema, dict):
        return [f"{location}: schema must be an object"]
    expected_type = schema.get("type")
    if not isinstance(expected_type, str) or expected_type not in {
        "object",
        "array",
        "string",
        "integer",
        "number",
        "boolean",
        "null",
    }:
        return [f"{location}: schema has an unsupported or missing type"]
    if not matches_type(instance, expected_type):
        return [f"{location}: expected {expected_type}"]
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{location}: value is outside enum")
    if expected_type == "object":
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        if not isinstance(required, list) or not all(isinstance(x, str) for x in required):
            errors.append(f"{location}: required must be a string array")
            return errors
        if not isinstance(properties, dict):
            errors.append(f"{location}: properties must be an object")
            return errors
        for key in required:
            if key not in instance:
                errors.append(f"{location}: missing required property {key}")
        for key, value in instance.items():
            if key in properties:
                errors.extend(validate_instance(value, properties[key], f"{location}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{location}: additional property {key} is not allowed")
    if expected_type == "array" and "items" in schema:
        for index, item in enumerate(instance):
            errors.extend(validate_instance(item, schema["items"], f"{location}[{index}]"))
    return errors


def validate_package(package_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    loaded: Dict[str, Any] = {}

    if not package_dir.is_dir():
        return [("CFD-PACKAGE-NOT-FOUND", f"not a directory: {package_dir}")]

    for key, (name, missing_code) in FILES.items():
        path = package_dir / name
        if not path.is_file():
            findings.append((missing_code, f"required file is missing: {name}"))
            loaded[key] = None
        else:
            loaded[key] = load_json(path, missing_code, findings)

    if loaded.get("constitution") is not None:
        require_object_keys(
            loaded["constitution"],
            CONSTITUTION_KEYS,
            "CFD-MISSING-CONSTITUTION",
            "constitution",
            findings,
        )
    if loaded.get("contract") is not None:
        require_object_keys(
            loaded["contract"],
            CONTRACT_KEYS,
            "CFD-MISSING-CONTRACT",
            "module contract",
            findings,
        )
    if loaded.get("constitution") is not None and loaded.get("contract") is not None:
        validate_completion_plan(loaded["constitution"], loaded["contract"], findings)

    schema = loaded.get("schema")
    if schema is not None:
        schema_shape_errors = validate_instance({}, schema)
        ignored_instance_errors = (
            schema_shape_errors
            and all("missing required property" in item for item in schema_shape_errors)
        )
        if schema_shape_errors and not ignored_instance_errors:
            findings.append(("CFD-INVALID-SCHEMA", "; ".join(schema_shape_errors)))

    if schema is not None and loaded.get("example") is not None:
        for error in validate_instance(loaded["example"], schema):
            findings.append(("CFD-EXAMPLE-SCHEMA-MISMATCH", error))

    golden = loaded.get("golden")
    if golden is not None:
        provenance = golden.get("source_provenance") if isinstance(golden, dict) else None
        trusted = (
            isinstance(golden, dict)
            and golden.get("oracle_type") == "manual"
            and isinstance(provenance, dict)
            and isinstance(provenance.get("source_id"), str)
            and bool(provenance.get("source_id"))
            and provenance.get("manual_reviewed") is True
            and provenance.get("generated_from_candidate") is False
            and isinstance(golden.get("decision_notes"), list)
            and bool(golden.get("decision_notes"))
        )
        if not trusted:
            findings.append(
                (
                    "CFD-UNTRUSTED-GOLDEN",
                    "golden must be manual, source-linked, reviewed, not candidate-generated, and include decision notes",
                )
            )
        if schema is not None and isinstance(golden, dict) and "artifact" in golden:
            for error in validate_instance(golden["artifact"], schema):
                findings.append(("CFD-UNTRUSTED-GOLDEN", f"golden artifact {error}"))

    acceptance = loaded.get("acceptance")
    if acceptance is not None:
        blocking = acceptance.get("blocking_checks") if isinstance(acceptance, dict) else None
        advisory = acceptance.get("advisory_checks") if isinstance(acceptance, dict) else None
        ceiling = acceptance.get("claim_ceiling") if isinstance(acceptance, dict) else None
        closeout = (
            acceptance.get("required_closeout_fields") if isinstance(acceptance, dict) else None
        )
        valid_lists = isinstance(blocking, list) and bool(blocking) and isinstance(advisory, list)
        ids: List[str] = []
        if valid_lists:
            entries = blocking + advisory
            valid_lists = all(
                isinstance(item, dict)
                and isinstance(item.get("id"), str)
                and isinstance(item.get("rule"), str)
                for item in entries
            )
            if valid_lists:
                ids = [item["id"] for item in entries]
        closeout_valid = (
            isinstance(closeout, list)
            and all(is_non_empty_string(item) for item in closeout)
            and REQUIRED_CLOSEOUT_FIELDS <= set(closeout)
        )
        if (
            not valid_lists
            or len(ids) != len(set(ids))
            or not is_non_empty_string(ceiling)
            or not closeout_valid
        ):
            findings.append(
                (
                    "CFD-MISSING-ACCEPTANCE-POLICY",
                    "acceptance policy must separate blocking/advisory checks, use unique IDs, state a claim ceiling, and require separate slice and Session closeout fields",
                )
            )

    return findings


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_contract_package.py <package-dir>", file=sys.stderr)
        return 2
    package_dir = Path(argv[1]).resolve()
    findings = validate_package(package_dir)
    if findings:
        for code, message in findings:
            print(f"{code}: {message}")
        return 1
    print(
        "CFD-VALID: contract package structure and declared relationships passed; "
        "semantic truth and production readiness are not established"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
