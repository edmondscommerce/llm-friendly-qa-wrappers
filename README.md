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
./wrappers/nodejs/eslint/run.sh src/
# ✅ ESLint: 0 errors (details: /tmp/eslint-xyz.json)

jq '.summary.error_count' /tmp/eslint-xyz.json
```

## Status

Initial project structure. Wrappers coming soon.
