# Plan 00005: Python Tool Wrappers

**Status**: Not Started
**Created**: 2026-02-17
**Owner**: TBD
**Priority**: Medium
**Recommended Executor**: Sonnet 4.5
**Execution Strategy**: Sub-Agent Orchestration
**Blocked By**: Plan 00001 (Proof of Concept)

## Overview

Implement wrappers for Python QA tools following the pattern from Plan 00001. Python tools generally have excellent programmatic APIs and native JSON support, making these wrappers straightforward. Each wrapper follows the `llm-{toolname}.py` convention.

## Goals

- Implement wrappers for major Python QA tools
- Create test fixtures for each tool
- Pass acceptance tests
- Use pyproject.toml for dependency management with Python >= 3.11

## Non-Goals

- Supporting Python < 3.11
- Wrapping Python build tools (setuptools, poetry CLI)
- Framework-specific tools (Django checks, Flask-specific linters)

## Context & Background

Python QA tools are particularly well-suited for wrapping because they generally have clean programmatic APIs and native JSON output. Many (ruff, mypy) already output JSON. Python is also the language used for the acceptance test harness (from Plan 00001), so there's good synergy.

## Tools to Wrap

| Tool | Category | Programmatic API / JSON? | Priority |
|------|----------|--------------------------|----------|
| Ruff | Linting + Formatting | Yes (--output-format json) | High |
| pytest | Testing | Yes (--tb=short, plugins) | High |
| MyPy | Type checking | Yes (--output json) | High |
| Black | Formatting | Yes (--check --diff) | Medium |
| Bandit | Security | Yes (--format json) | Medium |
| pyright | Type checking | Yes (--outputjson) | Low |

## Tasks

### Phase 1: High-Priority Tools

- [ ] ⬜ **Task 1.1**: Ruff wrapper (`llm-ruff.py`)
  - [ ] ⬜ Create `wrappers/python/ruff/` directory structure
  - [ ] ⬜ Build wrapper using `ruff check --output-format json`
  - [ ] ⬜ Define schema.json for linting results
  - [ ] ⬜ Create test fixtures (clean Python code, code with violations)
  - [ ] ⬜ Create examples/pass.json and examples/fail.json
  - [ ] ⬜ Create pyproject.toml with ruff dependency and Python >= 3.11
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.2**: pytest wrapper (`llm-pytest.py`)
  - [ ] ⬜ Create `wrappers/python/pytest/` directory structure
  - [ ] ⬜ Build wrapper capturing test results (consider pytest-json-report plugin)
  - [ ] ⬜ Define schema.json for test results (collected, passed, failed, errors, skipped)
  - [ ] ⬜ Create test fixtures (passing tests, failing tests, mixed)
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.3**: MyPy wrapper (`llm-mypy.py`)
  - [ ] ⬜ Create `wrappers/python/mypy/` directory structure
  - [ ] ⬜ Build wrapper using mypy's JSON output or programmatic API
  - [ ] ⬜ Define schema.json for type errors
  - [ ] ⬜ Create test fixtures (correctly typed code, code with type errors)
  - [ ] ⬜ Run acceptance tests

### Phase 2: Medium-Priority Tools

- [ ] ⬜ **Task 2.1**: Black wrapper (`llm-black.py`)
  - [ ] ⬜ Use `--check --diff` to detect formatting issues
  - [ ] ⬜ Parse diff output into structured JSON

- [ ] ⬜ **Task 2.2**: Bandit wrapper (`llm-bandit.py`)
  - [ ] ⬜ Use `--format json` for security issue results
  - [ ] ⬜ Schema should capture severity levels and confidence

### Phase 3: Integration & Validation

- [ ] ⬜ **Task 3.1**: Run full acceptance test suite across all Python wrappers
- [ ] ⬜ **Task 3.2**: Verify pyproject.toml dependencies install cleanly (uv or pip)
- [ ] ⬜ **Task 3.3**: Test with realistic Python projects

## Success Criteria

- [ ] All high-priority wrappers pass acceptance tests
- [ ] Each wrapper has pyproject.toml requiring Python >= 3.11
- [ ] Terminal output matches spec
- [ ] Exit codes correct for all scenarios
- [ ] JSON schemas are jq-friendly

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| pytest requires plugin for JSON output | Low | Medium | Use pytest-json-report or parse stdout |
| MyPy incremental cache affects results | Low | Low | Run with --no-incremental in wrapper |
| Ruff evolves rapidly, rules change | Low | Medium | Pin minimum version, test against it |

## Notes & Updates

### 2026-02-17
- Plan created; blocked by Plan 00001 proof of concept
- Python tools have the best JSON output support of any ecosystem
- Ruff is replacing many older tools (flake8, isort, etc.) - focus on modern tools
- pytest is the most complex wrapper due to test result diversity
