# LLM-Friendly QA Tool Wrappers

Standardized wrappers for QA and static analysis tools that produce **terse terminal output** and **detailed JSON logs** - designed for LLM agents, CI/CD pipelines, and automated code quality workflows.

## Why?

QA tools produce verbose, human-optimized output. LLMs and automated systems need structured data. These wrappers bridge the gap:

- **1 line on pass, 2-5 lines on fail** - no noise, just signal
- **Full JSON details** written to a temp file for programmatic access
- **Native JSON first** - uses each tool's own JSON output mode when available
- **jq-friendly** - query results with standard tooling

## Supported Tools

### Node.js

| Tool | Wrapper | Category | Native JSON |
|------|---------|----------|-------------|
| [ESLint](https://eslint.org/) | `llm-eslint.js` | Linting | Yes (`--format json`) |
| [Prettier](https://prettier.io/) | `llm-prettier.js` | Formatting | No |
| [Jest](https://jestjs.io/) | `llm-jest.js` | Testing | Yes (`--json`) |
| [TypeScript](https://www.typescriptlang.org/) | `llm-tsc.js` | Type checking | No |
| [Vitest](https://vitest.dev/) | `llm-vitest.js` | Testing | Yes (`--reporter=json`) |
| [Biome](https://biomejs.dev/) | `llm-biome.js` | Linting + Formatting | Yes (`--reporter=json`) |

### PHP

| Tool | Wrapper | Category | Native JSON |
|------|---------|----------|-------------|
| [PHPStan](https://phpstan.org/) | `llm-phpstan.php` | Static analysis | Yes (`--error-format=json`) |
| [PHP-CS-Fixer](https://cs.symfony.com/) | `llm-php-cs-fixer.php` | Code style | Yes (`--format=json`) |
| [PHPUnit](https://phpunit.de/) | `llm-phpunit.php` | Testing | No (JUnit XML) |

### Bash / Shell

| Tool | Wrapper | Category | Native JSON |
|------|---------|----------|-------------|
| [ShellCheck](https://www.shellcheck.net/) | `llm-shellcheck.py` | Linting | Yes (`-f json`) |
| [shfmt](https://github.com/mvdan/sh) | `llm-shfmt.py` | Formatting | No |

### Python

| Tool | Wrapper | Category | Native JSON |
|------|---------|----------|-------------|
| [Ruff](https://docs.astral.sh/ruff/) | `llm-ruff.py` | Linting + Formatting | Yes (`--output-format json`) |
| [pytest](https://pytest.org/) | `llm-pytest.py` | Testing | No |
| [MyPy](https://mypy-lang.org/) | `llm-mypy.py` | Type checking | Yes (`-O json`) |

## Quick Start

```bash
git clone https://github.com/edmondscommerce/llm-friendly-qa-wrappers.git
cd llm-friendly-qa-wrappers

# Install a wrapper's dependencies
cd wrappers/nodejs/eslint && npm install && cd -

# Run it
node wrappers/nodejs/eslint/llm-eslint.js src/
# ✅ ESLint: 0 errors (details: /tmp/eslint-abc123.json)

# Query the JSON output
jq '.[0].errorCount' /tmp/eslint-abc123.json
```

## Output Format

**Terminal** (terse):
```
✅ ESLint: 0 errors (details: /tmp/eslint-abc123.json)
```
```
❌ ESLint: 6 errors, 0 warnings in 1 files
   - src/app.js:1:1 no-var: Unexpected var, use let or const instead.
   - src/app.js:4:9 eqeqeq: Expected '===' and instead saw '=='.
   (details: /tmp/eslint-abc123.json)
```

**JSON** (detailed): Tool's native JSON format when available, or structured custom JSON. Every wrapper includes a `schema.json` documenting its output format.

**Exit codes**: `0` = pass, `1` = fail, `2` = error (misconfiguration, missing deps)

## Design Principles

- **Native JSON First**: If a tool has a `--json` or `--format json` flag, use it. Never reinvent the wheel.
- **Same-Language Wrappers**: ESLint wrapper in JavaScript, PHPStan wrapper in PHP, Ruff wrapper in Python.
- **Tool-Specific Schemas**: Each tool defines its own JSON structure - no forced standardization.
- **Modern Versions Only**: Node.js >= 20, PHP >= 8.2, Python >= 3.11.
- **No Shell Scripts**: Wrappers need native JSON handling. Bash tools are wrapped in Python.

## Project Structure

```
wrappers/
├── nodejs/           # ESLint, Prettier, Jest, TypeScript, Vitest, Biome
├── php/              # PHPStan, PHP-CS-Fixer, PHPUnit
├── bash/             # ShellCheck, shfmt (Python wrappers)
└── python/           # Ruff, pytest, MyPy

test-fixtures/        # Pass/fail fixtures for each tool
acceptance-tests/     # Cross-language test harness
```

Each wrapper directory contains:
```
wrappers/{lang}/{tool}/
├── llm-{tool}.{ext}    # Main wrapper
├── schema.json          # JSON output schema
├── package.json         # Dependencies (or composer.json / pyproject.toml)
└── examples/
    ├── pass.json        # Example passing output
    └── fail.json        # Example failing output
```

## Use Cases

- **LLM agents** (Claude Code, Cursor, Copilot) - parse QA results programmatically
- **CI/CD pipelines** - structured output for automated decision-making
- **Code review automation** - jq queries for specific error patterns
- **AI-assisted development** - feed structured QA data to language models
- **Monitoring dashboards** - aggregate JSON results across projects

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for wrapper requirements and the pull request checklist.

## License

MIT
