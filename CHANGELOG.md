# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-17

### Added
- ESLint wrapper (Node.js) - native JSON output via `--format json`
- Prettier wrapper (Node.js) - custom JSON (no native JSON mode)
- Jest wrapper (Node.js) - native JSON output via `--json`
- TypeScript/tsc wrapper (Node.js) - custom JSON (no native JSON mode)
- Vitest wrapper (Node.js) - native JSON output via `--reporter=json`
- Biome wrapper (Node.js) - native JSON output via `--reporter=json`
- PHPStan wrapper (PHP) - native JSON output via `--error-format=json`
- PHP-CS-Fixer wrapper (PHP) - native JSON output via `--format=json`
- PHPUnit wrapper (PHP) - JUnit XML converted to JSON
- ShellCheck wrapper (Bash/Python) - native JSON output via `-f json`
- shfmt wrapper (Bash/Python) - diff output parsed to JSON
- Ruff wrapper (Python) - native JSON output via `--output-format json`
- pytest wrapper (Python) - custom JSON (no native JSON mode)
- MyPy wrapper (Python) - native JSON output via `-O json`
- Python acceptance test harness for cross-language wrapper validation
- "Native JSON First" design principle in MISSION.md
- Claude Code Hooks Daemon integration with plan workflow
- Implementation plans (00001-00005) for proof of concept and all languages
- Release process documentation and `/release` skill
