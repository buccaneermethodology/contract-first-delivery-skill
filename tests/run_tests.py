#!/usr/bin/env python3
"""Regression tests for the contract package validator."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "minimal-contract"
VALIDATOR = ROOT / "scripts" / "validate_contract_package.py"


def run_validator(package: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(package)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def rewrite_json(path: Path, change: Callable[[dict], None]) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    change(value)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def expect_failure(name: str, expected_code: str, mutate: Callable[[Path], None]) -> None:
    with tempfile.TemporaryDirectory(prefix="cfd-test-") as temporary:
        package = Path(temporary) / "minimal-contract"
        shutil.copytree(FIXTURE, package)
        mutate(package)
        result = run_validator(package)
        assert result.returncode != 0, f"{name}: validator unexpectedly passed\n{result.stdout}"
        assert expected_code in result.stdout, (
            f"{name}: expected {expected_code}\noutput:\n{result.stdout}"
        )


def main() -> int:
    positive = run_validator(FIXTURE)
    assert positive.returncode == 0, positive.stdout
    assert "CFD-VALID" in positive.stdout

    cases = [
        (
            "missing constitution",
            "CFD-MISSING-CONSTITUTION",
            lambda package: (package / "constitution.json").unlink(),
        ),
        (
            "missing module contract",
            "CFD-MISSING-CONTRACT",
            lambda package: (package / "module-contract.json").unlink(),
        ),
        (
            "invalid schema",
            "CFD-INVALID-SCHEMA",
            lambda package: rewrite_json(
                package / "artifact.schema.json", lambda value: value.update(type="mystery")
            ),
        ),
        (
            "example violates schema",
            "CFD-EXAMPLE-SCHEMA-MISMATCH",
            lambda package: rewrite_json(
                package / "example.valid.json", lambda value: value.pop("summary")
            ),
        ),
        (
            "golden lacks trusted provenance",
            "CFD-UNTRUSTED-GOLDEN",
            lambda package: rewrite_json(
                package / "golden.json",
                lambda value: value["source_provenance"].update(
                    manual_reviewed=False, generated_from_candidate=True
                ),
            ),
        ),
        (
            "missing acceptance policy",
            "CFD-MISSING-ACCEPTANCE-POLICY",
            lambda package: (package / "acceptance-policy.json").unlink(),
        ),
        (
            "acceptance categories collapse",
            "CFD-MISSING-ACCEPTANCE-POLICY",
            lambda package: rewrite_json(
                package / "acceptance-policy.json",
                lambda value: value.pop("advisory_checks"),
            ),
        ),
    ]
    for name, code, mutation in cases:
        expect_failure(name, code, mutation)
        print(f"PASS: {name} -> {code}")

    print(f"PASS: positive fixture and {len(cases)} fail-closed cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
