#!/usr/bin/env python3
"""
Acceptance test harness for QA tool wrappers.

Validates that a wrapper:
1. Produces correct exit codes (0=pass, 1=fail, 2=error)
2. Outputs terse terminal text matching expected format
3. Writes JSON to a temp file that validates against schema.json

The harness is format-agnostic - it does NOT assume any particular JSON
structure. Tools with native JSON output will have their own format.
Schema validation is the single source of truth for JSON correctness.

Usage:
    python run_acceptance.py <wrapper_dir> <fixture_dir>

Example:
    python run_acceptance.py wrappers/nodejs/eslint test-fixtures/nodejs/eslint
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import jsonschema


class AcceptanceResult:
    def __init__(self, name: str):
        self.name = name
        self.checks: list[tuple[str, bool, str]] = []

    def check(self, label: str, passed: bool, detail: str = "") -> None:
        self.checks.append((label, passed, detail))

    @property
    def passed(self) -> bool:
        return all(ok for _, ok, _ in self.checks)

    def report(self) -> str:
        lines = [f"\n{'=' * 60}", f"  {self.name}", f"{'=' * 60}"]
        for label, ok, detail in self.checks:
            icon = "PASS" if ok else "FAIL"
            line = f"  [{icon}] {label}"
            if detail:
                line += f" - {detail}"
            lines.append(line)
        status = "PASSED" if self.passed else "FAILED"
        lines.append(f"\n  Result: {status}")
        return "\n".join(lines)


def find_json_path(output: str) -> str | None:
    """Extract the JSON details path from wrapper output."""
    match = re.search(r"\(details:\s+(/\S+\.json)\)", output)
    return match.group(1) if match else None


def test_pass_fixture(
    wrapper_cmd: list[str], fixture_dir: Path, schema: dict
) -> AcceptanceResult:
    """Test wrapper against passing fixture."""
    result = AcceptanceResult("Pass Fixture")

    proc = subprocess.run(
        wrapper_cmd + ["src/"],
        capture_output=True,
        text=True,
        cwd=str(fixture_dir),
        timeout=30,
    )
    combined = proc.stdout + proc.stderr

    # Exit code should be 0
    result.check("Exit code is 0", proc.returncode == 0, f"got {proc.returncode}")

    # Output should contain success marker
    result.check(
        "Output contains success marker",
        "\u2705" in combined,
        repr(combined[:100]),
    )

    # Should be single line (terse)
    output_lines = [line for line in combined.strip().split("\n") if line.strip()]
    result.check(
        "Output is terse (1 line)", len(output_lines) == 1, f"got {len(output_lines)} lines"
    )

    # JSON file should exist and validate against schema
    json_path = find_json_path(combined)
    result.check("JSON path found in output", json_path is not None)

    if json_path and os.path.exists(json_path):
        with open(json_path) as f:
            data = json.load(f)

        try:
            jsonschema.validate(data, schema)
            result.check("JSON validates against schema", True)
        except jsonschema.ValidationError as e:
            result.check("JSON validates against schema", False, str(e.message)[:100])

        # Verify it's valid JSON (non-empty)
        is_non_empty = (isinstance(data, list) and len(data) > 0) or (
            isinstance(data, dict) and len(data) > 0
        )
        result.check("JSON output is non-empty", is_non_empty)
    elif json_path:
        result.check("JSON file exists", False, f"{json_path} not found")

    return result


def test_fail_fixture(
    wrapper_cmd: list[str], fixture_dir: Path, schema: dict
) -> AcceptanceResult:
    """Test wrapper against failing fixture."""
    result = AcceptanceResult("Fail Fixture")

    proc = subprocess.run(
        wrapper_cmd + ["src/"],
        capture_output=True,
        text=True,
        cwd=str(fixture_dir),
        timeout=30,
    )
    combined = proc.stdout + proc.stderr

    # Exit code should be 1
    result.check("Exit code is 1", proc.returncode == 1, f"got {proc.returncode}")

    # Output should contain failure marker
    result.check(
        "Output contains failure marker",
        "\u274c" in combined,
        repr(combined[:100]),
    )

    # Should be 2-5 lines (terse but informative)
    output_lines = [line for line in combined.strip().split("\n") if line.strip()]
    result.check(
        "Output is terse (2-5 lines)",
        2 <= len(output_lines) <= 5,
        f"got {len(output_lines)} lines",
    )

    # JSON file should exist and validate
    json_path = find_json_path(combined)
    result.check("JSON path found in output", json_path is not None)

    if json_path and os.path.exists(json_path):
        with open(json_path) as f:
            data = json.load(f)

        try:
            jsonschema.validate(data, schema)
            result.check("JSON validates against schema", True)
        except jsonschema.ValidationError as e:
            result.check("JSON validates against schema", False, str(e.message)[:100])

        # Verify it's valid JSON (non-empty)
        is_non_empty = (isinstance(data, list) and len(data) > 0) or (
            isinstance(data, dict) and len(data) > 0
        )
        result.check("JSON output is non-empty", is_non_empty)
    elif json_path:
        result.check("JSON file exists", False, f"{json_path} not found")

    return result


def test_no_args(wrapper_cmd: list[str], wrapper_dir: Path) -> AcceptanceResult:
    """Test wrapper with no arguments (should exit 2)."""
    result = AcceptanceResult("No Args (Error Case)")

    proc = subprocess.run(
        wrapper_cmd,
        capture_output=True,
        text=True,
        cwd=str(wrapper_dir),
        timeout=30,
    )
    combined = proc.stdout + proc.stderr

    result.check("Exit code is 2", proc.returncode == 2, f"got {proc.returncode}")
    result.check("Output contains error marker", "\u274c" in combined, repr(combined[:100]))

    return result


def detect_wrapper_command(wrapper_dir: Path) -> list[str] | None:
    """Detect how to run the wrapper based on files present."""
    for f in wrapper_dir.iterdir():
        if f.name.startswith("llm-") and f.suffix == ".js":
            return ["node", str(f)]
        if f.name.startswith("llm-") and f.suffix == ".php":
            return ["php", str(f)]
        if f.name.startswith("llm-") and f.suffix == ".py":
            return ["python3", str(f)]
    return None


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <wrapper_dir> <fixture_dir>")
        return 2

    wrapper_dir = Path(sys.argv[1]).resolve()
    fixture_dir = Path(sys.argv[2]).resolve()

    # Detect wrapper command
    wrapper_cmd = detect_wrapper_command(wrapper_dir)
    if not wrapper_cmd:
        print(f"ERROR: No llm-*.{{js,php,py}} found in {wrapper_dir}")
        return 2

    # Load schema
    schema_path = wrapper_dir / "schema.json"
    if not schema_path.exists():
        print(f"ERROR: No schema.json found in {wrapper_dir}")
        return 2

    with open(schema_path) as f:
        schema = json.load(f)

    print(f"\nWrapper: {wrapper_cmd}")
    print(f"Fixtures: {fixture_dir}")
    print(f"Schema: {schema_path}")

    results: list[AcceptanceResult] = []

    # Test pass fixture
    pass_dir = fixture_dir / "pass"
    if pass_dir.exists():
        results.append(test_pass_fixture(wrapper_cmd, pass_dir, schema))

    # Test fail fixture
    fail_dir = fixture_dir / "fail"
    if fail_dir.exists():
        results.append(test_fail_fixture(wrapper_cmd, fail_dir, schema))

    # Test no-args error
    results.append(test_no_args(wrapper_cmd, wrapper_dir))

    # Report
    all_passed = True
    for r in results:
        print(r.report())
        if not r.passed:
            all_passed = False

    print(f"\n{'=' * 60}")
    if all_passed:
        print("  ALL ACCEPTANCE TESTS PASSED")
    else:
        print("  SOME ACCEPTANCE TESTS FAILED")
    print(f"{'=' * 60}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
