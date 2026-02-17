# Plan 00004: Bash Tool Wrappers

**Status**: Not Started
**Created**: 2026-02-17
**Owner**: TBD
**Priority**: Medium
**Recommended Executor**: Sonnet 4.5
**Execution Strategy**: Single-Threaded
**Blocked By**: Plan 00001 (Proof of Concept)

## Overview

Implement wrappers for Bash/Shell QA tools. This is a special case because the project convention says "no shell scripts" for wrappers due to JSON handling pain. However, Bash QA tools themselves need wrappers, and wrapping a Bash tool in Python or Node.js feels wrong.

The pragmatic approach: wrap Bash tools in Python (which has excellent JSON handling and subprocess management), since the alternative (Bash generating JSON) contradicts our design principles.

## Goals

- Implement wrappers for Bash/Shell QA tools
- Maintain the "no shell script wrappers" principle by using Python
- Create test fixtures with known shell script issues
- Pass acceptance tests

## Non-Goals

- Writing wrappers IN Bash (contradicts MISSION.md)
- Wrapping general-purpose Unix tools (grep, awk, etc.)
- Supporting non-Bash shells (zsh-specific, fish-specific tools)

## Context & Background

MISSION.md explicitly states "No shell scripts - Working with JSON in bash/shell is painful." This creates a philosophical question for Bash QA tools: what language do we wrap them in?

The answer is Python - it's the natural "glue language" for CLI tools, has excellent JSON support, and is already a project dependency (via the hooks daemon).

## Tools to Wrap

| Tool | Category | Output Format | Wrapper Language | Priority |
|------|----------|--------------|-----------------|----------|
| ShellCheck | Linting | JSON (-f json) | Python | High |
| shfmt | Formatting | Diff output | Python | Medium |
| bashate | Style checking | Text output | Python | Low |

## Tasks

### Phase 1: ShellCheck (Reference Bash Tool Wrapper)

- [ ] ⬜ **Task 1.1**: Install ShellCheck and verify availability
- [ ] ⬜ **Task 1.2**: Create `wrappers/bash/shellcheck/` directory structure
  - [ ] ⬜ Note: wrapper file is `llm-shellcheck.py` (Python, not Bash)
- [ ] ⬜ **Task 1.3**: Build `llm-shellcheck.py`
  - [ ] ⬜ Invoke shellcheck with `-f json` flag
  - [ ] ⬜ Transform ShellCheck JSON to our schema format
  - [ ] ⬜ Terse terminal output
  - [ ] ⬜ Correct exit codes
- [ ] ⬜ **Task 1.4**: Define schema.json for shell linting results
- [ ] ⬜ **Task 1.5**: Create test fixtures
  - [ ] ⬜ `test-fixtures/bash/shellcheck/pass/` - Clean shell scripts
  - [ ] ⬜ `test-fixtures/bash/shellcheck/fail/` - Scripts with SC warnings (unquoted vars, etc.)
- [ ] ⬜ **Task 1.6**: Create examples and README
- [ ] ⬜ **Task 1.7**: Create pyproject.toml with dependencies
- [ ] ⬜ **Task 1.8**: Run acceptance tests

### Phase 2: Additional Tools

- [ ] ⬜ **Task 2.1**: shfmt wrapper (`llm-shfmt.py`)
  - [ ] ⬜ shfmt uses diff output for formatting checks
  - [ ] ⬜ Need to parse diff into structured JSON

- [ ] ⬜ **Task 2.2**: bashate wrapper (`llm-bashate.py`)
  - [ ] ⬜ Text-based output, needs parsing

### Phase 3: Validation

- [ ] ⬜ **Task 3.1**: Run acceptance tests for all Bash tool wrappers
- [ ] ⬜ **Task 3.2**: Document the "Bash tools wrapped in Python" convention

## Technical Decisions

### Decision 1: Wrapper Language for Bash Tools
**Context**: MISSION.md says wrappers should be in the same language as the tool, but also says no shell scripts.
**Options Considered**:
1. Python wrappers - excellent JSON, subprocess, already available
2. Bash wrappers - native but JSON handling is painful
3. Node.js wrappers - possible but Python is more natural for CLI tools
**Decision**: Python. The "same language" rule exists for native JSON handling. Since Bash can't do JSON well, Python is the pragmatic choice.
**Date**: 2026-02-17

## Success Criteria

- [ ] ShellCheck wrapper passes all acceptance tests
- [ ] Convention for "Bash tools in Python" is documented
- [ ] Test fixtures demonstrate real shell scripting issues
- [ ] Exit codes and output format match spec

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| ShellCheck not available on all platforms | Low | Low | Document install instructions per OS |
| shfmt diff parsing is fragile | Medium | Medium | Use shfmt -d exit code + count changed files |
| Convention confusion (Python wrapper for Bash tool) | Low | Medium | Clear documentation in wrapper README |

## Notes & Updates

### 2026-02-17
- Plan created; blocked by Plan 00001 proof of concept
- ShellCheck is the clear priority - most widely used Bash linter
- Python chosen as wrapper language due to JSON handling requirements
- Directory is `wrappers/bash/` (by tool ecosystem) but files are `.py`
