#!/usr/bin/env python3
"""
shfmt wrapper with diff-based JSON output.

shfmt has no native JSON output mode, so this wrapper runs shfmt -d
to get diff output and parses it into structured JSON.
"""

import json
import re
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


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def parse_diff(diff_text: str) -> list[dict]:
    """Parse unified diff output into structured file results."""
    diff_text = strip_ansi(diff_text)
    files: dict[str, list[dict]] = {}
    current_file = None

    for line in diff_text.splitlines():
        # Match diff header: --- path.orig / +++ path
        orig_match = re.match(r"^--- (.+)\.orig$", line)
        if orig_match:
            current_file = orig_match.group(1)
            if current_file not in files:
                files[current_file] = []
            continue

        # Match hunk header: @@ -start,count +start,count @@
        hunk_match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", line)
        if hunk_match and current_file:
            files[current_file].append({
                "original_start": int(hunk_match.group(1)),
                "original_count": int(hunk_match.group(2) or 1),
                "formatted_start": int(hunk_match.group(3)),
                "formatted_count": int(hunk_match.group(4) or 1),
            })

    results = []
    for file_path, hunks in files.items():
        results.append({
            "file_path": file_path,
            "formatted": False,
            "diff_count": len(hunks),
            "hunks": hunks,
        })
    return results


def get_shfmt_version() -> str:
    try:
        proc = subprocess.run(
            ["shfmt", "--version"], capture_output=True, text=True, timeout=10
        )
        return proc.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def main() -> int:
    targets = sys.argv[1:]

    if not targets:
        sys.stderr.write("❌ shfmt: No targets specified\n")
        sys.stderr.write("   Usage: llm-shfmt.py <path> [...paths]\n")
        return 2

    files = find_shell_files(targets)
    if not files:
        sys.stderr.write("❌ shfmt: No shell files found\n")
        return 2

    try:
        proc = subprocess.run(
            ["shfmt", "-d"] + files,
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        sys.stderr.write("❌ shfmt: shfmt not found in PATH\n")
        return 2
    except subprocess.TimeoutExpired:
        sys.stderr.write("❌ shfmt: Execution timed out\n")
        return 2

    # shfmt -d exits 0 if all formatted, 1 if diffs found
    diff_output = proc.stdout
    has_diffs = proc.returncode != 0

    if has_diffs:
        unformatted = parse_diff(diff_output)
    else:
        unformatted = []

    # Build results for all files
    unformatted_paths = {r["file_path"] for r in unformatted}
    results = []
    for f in files:
        if f in unformatted_paths:
            results.append(next(r for r in unformatted if r["file_path"] == f))
        else:
            results.append({
                "file_path": f,
                "formatted": True,
                "diff_count": 0,
                "hunks": [],
            })

    unformatted_count = len(unformatted_paths)

    output = {
        "tool": "shfmt",
        "version": get_shfmt_version(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exit_code": 1 if unformatted_count > 0 else 0,
        "command": f"shfmt -d {' '.join(targets)}",
        "summary": {
            "total_files": len(files),
            "files_with_errors": unformatted_count,
            "error_count": unformatted_count,
            "warning_count": 0,
        },
        "results": results,
    }

    tmp = tempfile.NamedTemporaryFile(
        prefix="shfmt-", suffix=".json", delete=False, mode="w"
    )
    json.dump(output, tmp, indent=2)
    tmp.close()

    if unformatted_count == 0:
        sys.stdout.write(
            f"✅ shfmt: All {len(files)} files formatted (details: {tmp.name})\n"
        )
        return 0
    else:
        sys.stdout.write(
            f"❌ shfmt: {unformatted_count} of {len(files)} files need formatting\n"
        )
        for r in unformatted[:3]:
            sys.stdout.write(f"   - {r['file_path']}\n")
        sys.stdout.write(f"   (details: {tmp.name})\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
