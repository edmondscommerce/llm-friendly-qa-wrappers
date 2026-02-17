#!/usr/bin/env python3
"""
Ruff wrapper using native JSON output (--output-format json).

Ruff provides rich JSON output natively, so we use it directly
rather than reconstructing JSON from the programmatic API.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def main() -> int:
    targets = sys.argv[1:]

    if not targets:
        sys.stderr.write("❌ Ruff: No targets specified\n")
        sys.stderr.write("   Usage: llm-ruff.py <path> [...paths]\n")
        return 2

    try:
        cmd = ["ruff", "check", "--output-format", "json", *targets]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if proc.returncode not in (0, 1):
            msg = proc.stderr.strip() or proc.stdout.strip()
            sys.stderr.write(f"❌ Ruff: Execution error - {msg[:200]}\n")
            return 2

        results = json.loads(proc.stdout) if proc.stdout.strip() else []

        error_count = len(results)
        files_with_errors = len({r["filename"] for r in results})

        output = {
            "tool": "ruff",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": " ".join(cmd),
            "summary": {
                "error_count": error_count,
                "files_with_errors": files_with_errors,
            },
            "results": results,
        }

        tmp = tempfile.NamedTemporaryFile(
            prefix="ruff-", suffix=".json", delete=False, mode="w"
        )
        json.dump(output, tmp, indent=2)
        tmp.close()

        if error_count == 0:
            sys.stdout.write(f"✅ Ruff: 0 errors (details: {tmp.name})\n")
            return 0
        else:
            sys.stdout.write(
                f"❌ Ruff: {error_count} errors in {files_with_errors} files\n"
            )
            for issue in results[:3]:
                loc = issue["location"]
                sys.stdout.write(
                    f"   - {issue['filename']}:{loc['row']}:{loc['column']} "
                    f"{issue['code']}: {issue['message']}\n"
                )
            sys.stdout.write(f"   (details: {tmp.name})\n")
            return 1

    except FileNotFoundError:
        sys.stderr.write("❌ Ruff: ruff not found. Install with: pip install ruff\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"❌ Ruff: Execution error - {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
