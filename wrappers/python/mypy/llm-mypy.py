#!/usr/bin/env python3
"""
MyPy wrapper using native JSON output (-O json).

MyPy provides JSON output natively with -O json, outputting one
JSON object per line (JSONL). We collect and wrap these in an envelope.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def main() -> int:
    targets = sys.argv[1:]

    if not targets:
        sys.stderr.write("❌ MyPy: No targets specified\n")
        sys.stderr.write("   Usage: llm-mypy.py <path> [...paths]\n")
        return 2

    try:
        cmd = ["mypy", "-O", "json", "--no-error-summary", *targets]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if proc.returncode not in (0, 1):
            msg = proc.stderr.strip() or proc.stdout.strip()
            sys.stderr.write(f"❌ MyPy: Execution error - {msg[:200]}\n")
            return 2

        # Parse JSONL output (one JSON object per line)
        results = []
        for line in proc.stdout.strip().splitlines():
            line = line.strip()
            if line:
                results.append(json.loads(line))

        error_count = sum(1 for r in results if r.get("severity") == "error")
        note_count = sum(1 for r in results if r.get("severity") == "note")
        files_with_errors = len({
            r["file"] for r in results if r.get("severity") == "error"
        })

        output = {
            "tool": "mypy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": " ".join(cmd),
            "summary": {
                "error_count": error_count,
                "note_count": note_count,
                "files_with_errors": files_with_errors,
            },
            "results": results,
        }

        tmp = tempfile.NamedTemporaryFile(
            prefix="mypy-", suffix=".json", delete=False, mode="w"
        )
        json.dump(output, tmp, indent=2)
        tmp.close()

        if error_count == 0:
            sys.stdout.write(f"✅ MyPy: 0 errors (details: {tmp.name})\n")
            return 0
        else:
            sys.stdout.write(
                f"❌ MyPy: {error_count} errors in {files_with_errors} files\n"
            )
            errors = [r for r in results if r.get("severity") == "error"]
            for e in errors[:3]:
                sys.stdout.write(
                    f"   - {e['file']}:{e['line']}:{e['column']} "
                    f"[{e.get('code', '?')}] {e['message']}\n"
                )
            sys.stdout.write(f"   (details: {tmp.name})\n")
            return 1

    except FileNotFoundError:
        sys.stderr.write("❌ MyPy: mypy not found. Install with: pip install mypy\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"❌ MyPy: Execution error - {e}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())
