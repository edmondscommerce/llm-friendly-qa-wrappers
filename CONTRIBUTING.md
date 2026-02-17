# Contributing Guide

## Wrapper Requirements

### Language Choice

Wrappers **must** be written in the same language as the tool they wrap:

- ✅ ESLint wrapper in JavaScript/TypeScript
- ✅ PHPStan wrapper in PHP
- ✅ pytest wrapper in Python
- ❌ Any wrapper in bash/shell (JSON handling is too painful)

### Naming Convention

All wrapper files follow the pattern: **`llm-{toolname}.{ext}`**

Examples:
- Node.js: `llm-eslint.js`, `llm-prettier.js`, `llm-jest.js`
- PHP: `llm-phpstan.php`, `llm-php-cs-fixer.php`
- Python: `llm-ruff.py`, `llm-pytest.py`, `llm-mypy.py`

### Directory Structure

Each wrapper must include:

```
wrappers/{language}/{tool}/
├── llm-{tool}.{ext}    # Main wrapper file
├── package.json        # Language package file (package.json, composer.json, pyproject.toml)
├── schema.json         # JSON schema for output
├── README.md           # Usage documentation
└── examples/
    ├── pass.json       # Example successful run
    └── fail.json       # Example failed run
```

**Example for ESLint:**
```
wrappers/nodejs/eslint/
├── llm-eslint.js
├── package.json
├── schema.json
├── README.md
└── examples/
    ├── pass.json
    └── fail.json
```

### Minimum Version Requirements

**We only support modern versions** - no legacy support.

Document minimum versions in package files:

**Node.js** (`package.json`):
```json
{
  "engines": {
    "node": ">=20.0.0"
  }
}
```

**PHP** (`composer.json`):
```json
{
  "require": {
    "php": ">=8.2"
  }
}
```

**Python** (`pyproject.toml`):
```toml
[project]
requires-python = ">=3.11"
```

### Output Requirements

#### Terminal Output (stdout/stderr)

**Success** (single line):
```
✅ [Tool]: [Summary] (details: [json-path])
```

**Failure** (2-5 lines):
```
❌ [Tool]: [Brief summary]
   - [Key issue 1]
   - [Key issue 2]
   (details: [json-path])
```

#### JSON Output (file)

- Write to temporary file (use language's temp file API)
- Follow schema defined in `schema.json`
- Use semantic keys (e.g., `error_count` not `errors`)
- Design for jq queries

### Exit Codes

- `0`: All checks passed
- `1`: Checks failed (errors found)
- `2`: Tool execution error (misconfiguration, missing deps, etc.)

### Schema Design Guidelines

1. **Use semantic keys**: `error_count`, `file_path`, `line_number`
2. **Avoid abbreviations**: `message` not `msg`, `severity` not `sev`
3. **Flat when possible**: Deeply nested objects are hard to query
4. **Arrays for collections**: Use arrays for lists of errors/files
5. **Include metadata**: Tool version, timestamp, command executed

### Example Schema Template

```json
{
  "tool": "toolname",
  "version": "1.2.3",
  "timestamp": "2026-02-17T10:30:45Z",
  "exit_code": 1,
  "command": "toolname --flag arg",
  "summary": {
    "total_files": 10,
    "files_with_errors": 2,
    "error_count": 5,
    "warning_count": 3
  },
  "results": [
    {
      "file_path": "src/app.js",
      "errors": [
        {
          "line": 15,
          "column": 8,
          "severity": "error",
          "rule": "rule-name",
          "message": "Error description"
        }
      ]
    }
  ]
}
```

### README Template

Each wrapper's README should include:

```markdown
# [Tool Name] Wrapper

## Requirements

- [Language]: >= [version]
- [Tool]: >= [version]

## Installation

[Installation steps]

## Usage

[Usage examples]

## Output Schema

See [schema.json](schema.json) for complete schema.

## Examples

- [pass.json](examples/pass.json): Successful run
- [fail.json](examples/fail.json): Failed run with errors
```

### Testing

Before submitting:

1. Test with passing code (verify `pass.json` format)
2. Test with failing code (verify `fail.json` format)
3. Validate JSON output against schema
4. Test jq queries work as expected
5. Verify exit codes are correct

### Pull Request Checklist

- [ ] Wrapper file named `llm-{toolname}.{ext}`
- [ ] Wrapper written in same language as tool
- [ ] Minimum version documented in package file
- [ ] `schema.json` present and valid
- [ ] `README.md` with usage instructions
- [ ] `examples/pass.json` and `examples/fail.json` included
- [ ] Terminal output is terse (1-5 lines max)
- [ ] JSON output matches schema
- [ ] Exit codes correct (0 = pass, 1 = fail, 2 = error)
- [ ] Tested with real code samples

## Questions?

Open an issue for discussion before starting work on a new wrapper.
