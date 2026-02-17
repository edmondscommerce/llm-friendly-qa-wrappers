# Mission

## Problem

QA tools produce verbose output optimized for humans. Parsing this output programmatically is difficult.

## Solution

Thin wrappers that separate concerns:
- **Terminal**: Terse pass/fail summary
- **JSON file**: Complete structured details

## Design Principles

### Terse Terminal Output

Success: `✅ [Tool]: [Summary] (details: [path])`

Failure: `❌ [Tool]: [Summary] (details: [path])`

### Detailed JSON Logs

Standard schema across all tools:

```json
{
  "metadata": {
    "tool": "eslint",
    "version": "8.56.0",
    "timestamp": "2026-02-17T10:30:45Z",
    "exit_code": 1
  },
  "summary": {
    "error_count": 3,
    "warning_count": 7,
    "passed": false
  },
  "details": []
}
```

### JQ-Friendly

Semantic keys optimized for queries:

```bash
jq '.summary.error_count' result.json
jq '.details[] | select(.severity == "error")' result.json
```

## Target Languages

Phase 1: Node.js, PHP
Future: Python, Ruby, Go, Rust

## Use Cases

- Quick status checks
- Automated analysis of QA results
- CI/CD integration
- Scriptable queries

## Contributing

Each wrapper must:
1. Follow the schema
2. Produce terse terminal output
3. Write JSON to temp file
4. Be jq-friendly
