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

## Minimum Versions

We support **modern versions only** - no legacy support.

Document minimum versions in each wrapper's package file:
- Node.js: `package.json` → `"engines": {"node": ">=20.0.0"}`
- PHP: `composer.json` → `"require": {"php": ">=8.2"}`
- Python: `pyproject.toml` → `requires-python = ">=3.11"`

## Usage Example

### Node.js (ESLint)
```bash
node wrappers/nodejs/eslint/wrapper.js src/
# ✅ ESLint: 0 errors (details: /tmp/eslint-xyz.json)

jq '.summary.error_count' /tmp/eslint-xyz.json
```

### PHP (PHPStan)
```bash
php wrappers/php/phpstan/wrapper.php src/
# ❌ PHPStan: 5 errors (details: /tmp/phpstan-xyz.json)

jq '.errors[] | .message' /tmp/phpstan-xyz.json
```

## Use Cases

- Quick status checks
- Automated analysis of QA results
- CI/CD integration
- Scriptable queries with jq

## Wrapper Structure

Wrappers are written in the **same language as the tool they wrap**.

- Node.js tools (ESLint, Prettier, Jest) → JavaScript/TypeScript wrappers
- PHP tools (PHPStan, PHP-CS-Fixer) → PHP wrappers
- Python tools (pytest, ruff, mypy) → Python wrappers

**Why?** Native JSON handling, proper error handling, language-specific features.

**No shell scripts** - Working with JSON in bash/shell is painful.

Each tool wrapper directory contains:

```
wrappers/nodejs/eslint/
├── wrapper.js          # Main wrapper (NOT bash)
├── package.json        # Dependencies + minimum Node version
├── schema.json         # JSON schema for output
├── README.md           # Usage documentation
└── examples/
    ├── pass.json       # Example passing result
    └── fail.json       # Example failing result
```

Example for PHP:
```
wrappers/php/phpstan/
├── wrapper.php         # Main wrapper
├── composer.json       # Dependencies + minimum PHP version
├── schema.json         # JSON schema
├── README.md           # Usage docs
└── examples/
    ├── pass.json
    └── fail.json
```

## Contributing

Each wrapper must:
1. Define its own JSON schema (schema.json)
2. Produce terse terminal output
3. Write JSON to temp file matching schema
4. Use semantic keys (jq-friendly)
5. Include example outputs
