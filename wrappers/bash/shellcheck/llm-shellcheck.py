#!/usr/bin/env python3
"""
ShellCheck wrapper using native JSON output (-f json).

ShellCheck provides rich JSON output natively, so we use it directly
rather than reconstructing JSON from a programmatic API. The wrapper
adds a thin envelope with metadata around the native output.
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def find_shell_files(targets: list[str]) -> list[str]:
    """Find shell script files in the given targets."""
    extensions = {".sh", ".bash", ".ksh", ".zsh"}
    files: list[str] = []

    for target in targets:
        p = Path(target)
        if p.is_file():
            files.append(str(p.resolve()))
        elif p.is_dir():
            for ext in extensions:
                files.extend(str(f.resolve()) for f in p.rglob(f"*{ext}"))
    return sorted(files)


def get_shellcheck_version() -> str:
    try:
        proc = subprocess.run(
            ["shellcheck", "--version"], capture_output=True, text=True, timeout=10
        )
        for line in proc.stdout.splitlines():
            if line.startswith("version:"):
                return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "unknown"


def main() -> int:
    targets = sys.argv[1:]

    if not targets:
        sys.stderr.write("❌ ShellCheck: No targets specified\n")
        sys.stderr.write("   Usage: llm-shellcheck.py <path> [...paths]\n")
        return 2

    files = find_shell_files(targets)
    if not files:
        sys.stderr.write("❌ ShellCheck: No shell files found\n")
        return 2

    try:
        proc = subprocess.run(
            ["shellcheck", "-f", "json"] + files,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        sys.stderr.write("❌ ShellCheck: shellcheck not found in PATH\n")
        return 2
    except subprocess.TimeoutExpired:
        sys.stderr.write("❌ ShellCheck: Execution timed out\n")
        return 2

    # ShellCheck outputs JSON to stdout, even on failure
    try:
        issues = json.loads(proc.stdout) if proc.stdout.strip() else []
    except json.JSONDecodeError:
        sys.stderr.write("❌ ShellCheck: Failed to parse JSON output\n")
        return 2

    error_count = sum(1 for r in issues if r.get("level") == "error")
    warning_count = sum(1 for r in issues if r.get("level") == "warning")
    info_count = sum(1 for r in issues if r.get("level") == "info")
    style_count = sum(1 for r in issues if r.get("level") == "style")

    output = {
        "tool": "shellcheck",
        "version": get_shellcheck_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exit_code": 0 if len(issues) == 0 else 1,
        "command": f"shellcheck -f json {' '.join(targets)}",
        "summary": {
            "total_files": len(files),
            "total_issues": len(issues),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "style_count": style_count,
        },
        "issues": issues,
    }

    # Write JSON output to temp file
    tmp = tempfile.NamedTemporaryFile(
        prefix="shellcheck-", suffix=".json", delete=False, mode="w"
    )
    json.dump(output, tmp, indent=2)
    tmp.close()

    if len(issues) == 0:
        sys.stdout.write(
            f"✅ ShellCheck: 0 issues in {len(files)} files (details: {tmp.name})\n"
        )
        return 0
    else:
        total_issues = len(issues)
        sys.stdout.write(
            f"❌ ShellCheck: {total_issues} issues ({error_count} errors, "
            f"{warning_count} warnings, {info_count} info)\n"
        )
        # Show up to 3 top issues
        for issue in issues[:3]:
            sys.stdout.write(
                f"   - {issue['file']}:{issue['line']} SC{issue['code']}: "
                f"{issue['message']}\n"
            )
        sys.stdout.write(f"   (details: {tmp.name})\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
