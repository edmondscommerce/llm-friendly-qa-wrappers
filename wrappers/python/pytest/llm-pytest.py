#!/usr/bin/env python3
"""
pytest wrapper with custom JSON output.

pytest does not provide native JSON output, so this wrapper
parses the result and constructs structured JSON.
"""

import json
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def parse_pytest_output(stdout: str, stderr: str) -> dict:
    """Parse pytest verbose output into structured data."""
    lines = stdout.splitlines()
    tests = []
    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    # Parse individual test results from -v output
    for line in lines:
        # Matches lines like: src/test_clean.py::test_addition PASSED
        match = re.match(r"^(.+?)::(\S+)\s+(PASSED|FAILED|ERROR|SKIPPED)", line)
        if match:
            file_path, test_name, status = match.groups()
            status_lower = status.lower()
            tests.append({
                "file_path": file_path,
                "test_name": test_name,
                "status": status_lower,
            })
            if status == "PASSED":
                passed += 1
            elif status == "FAILED":
                failed += 1
            elif status == "ERROR":
                errors += 1
            elif status == "SKIPPED":
                skipped += 1

    # Parse failure details from FAILURES section
    failure_details = []
    in_failures = False
    current_failure = None
    for line in lines:
        if line.startswith("_ _ _ _ _") or line.startswith("FAILED"):
            continue
        if line.startswith("=") and "FAILURES" in line:
            in_failures = True
            continue
        if line.startswith("=") and in_failures:
            in_failures = False
            continue
        if in_failures and line.startswith("___") and "___" in line:
            name = line.strip("_ ").strip()
            current_failure = {"test_name": name, "details": []}
            failure_details.append(current_failure)
            continue
        if in_failures and current_failure is not None:
            current_failure["details"].append(line)

    for fd in failure_details:
        fd["details"] = "\n".join(fd["details"]).strip()

    # Parse summary line: "2 failed, 1 passed"
    summary_match = re.search(r"=+ (.+) =+\s*$", stdout, re.MULTILINE)
    summary_line = summary_match.group(1) if summary_match else ""

    return {
        "tool": "pytest",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total": passed + failed + errors + skipped,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "summary_line": summary_line,
        },
        "tests": tests,
        "failures": failure_details,
    }


def main() -> int:
    targets = sys.argv[1:]

    if not targets:
        sys.stderr.write("❌ pytest: No targets specified\n")
        sys.stderr.write("   Usage: llm-pytest.py <path> [...paths]\n")
        return 2

    try:
        proc = subprocess.run(
            ["python3", "-m", "pytest", "-v", "--tb=short", "--no-header", "--color=no", *targets],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode not in (0, 1):
            msg = proc.stderr.strip() or proc.stdout.strip()
            sys.stderr.write(f"❌ pytest: Execution error - {msg[:200]}\n")
            return 2

        result = parse_pytest_output(proc.stdout, proc.stderr)

        tmp = tempfile.NamedTemporaryFile(
            prefix="pytest-", suffix=".json", delete=False, mode="w"
        )
        json.dump(result, tmp, indent=2)
        tmp.close()

        s = result["summary"]
        if s["failed"] == 0 and s["errors"] == 0:
            sys.stdout.write(
                f"✅ pytest: {s['passed']} passed (details: {tmp.name})\n"
            )
            return 0
        else:
            sys.stdout.write(
                f"❌ pytest: {s['failed']} failed, {s['passed']} passed\n"
            )
            for f in result["failures"][:3]:
                sys.stdout.write(f"   - {f['test_name']}\n")
            sys.stdout.write(f"   (details: {tmp.name})\n")
            return 1

    except FileNotFoundError:
        sys.stderr.write("❌ pytest: pytest not found. Install with: pip install pytest\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"❌ pytest: Execution error - {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
