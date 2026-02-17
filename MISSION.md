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

Each tool defines its own JSON schema - no forced standardization across tools.

### Tool-Specific Schema

Each wrapper directory contains:
- **Wrapper script**: Runs the tool and produces output
- **JSON schema file**: Documents the JSON structure
- **Example outputs**: Sample JSON files showing real results

### JQ-Friendly

Design schemas with semantic keys for easy querying:

```bash
jq '.error_count' result.json
jq '.files[] | select(.errors > 0)' result.json
```

## Target Languages

Phase 1: Node.js, PHP
Future: Python, Ruby, Go, Rust

## Use Cases

- Quick status checks
- Automated analysis of QA results
- CI/CD integration
- Scriptable queries

## Wrapper Structure

Each tool wrapper directory contains:

```
wrappers/nodejs/eslint/
├── run.sh              # Wrapper script
├── schema.json         # JSON schema for output
└── examples/
    ├── pass.json       # Example passing result
    └── fail.json       # Example failing result
```

## Contributing

Each wrapper must:
1. Define its own JSON schema (schema.json)
2. Produce terse terminal output
3. Write JSON to temp file matching schema
4. Use semantic keys (jq-friendly)
5. Include example outputs
