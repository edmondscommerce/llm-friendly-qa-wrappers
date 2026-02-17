# QA Tool Wrappers

Standardized wrappers for QA tools with terse terminal output and detailed JSON logs.

## Purpose

See [MISSION.md](MISSION.md) for complete details.

This project wraps common QA tools to provide:
- **Terse stdout/stderr**: 1 line on pass, few lines on fail
- **Detailed JSON logs**: Structured output in temporary files
- **Tool-specific schemas**: Each tool defines its own JSON structure
- **Example outputs**: Sample JSON files for reference
- **JQ-friendly**: Semantic keys for easy querying

## Structure

```
wrappers/
├── nodejs/          # Node.js tools
└── php/             # PHP tools
```

## Quick Example

```bash
# Run wrapper in native language (NOT shell)
node wrappers/nodejs/eslint/wrapper.js src/
# ✅ ESLint: 0 errors (details: /tmp/eslint-xyz.json)

# Query structured results
jq '.summary.error_count' /tmp/eslint-xyz.json
```

## Implementation

Wrappers are written in the **same language as the tool**:
- Node.js tools → JavaScript/TypeScript wrappers
- PHP tools → PHP wrappers
- Python tools → Python wrappers

**No shell scripts** - Native JSON handling is essential.

## Status

Initial project structure. Wrappers coming soon.
