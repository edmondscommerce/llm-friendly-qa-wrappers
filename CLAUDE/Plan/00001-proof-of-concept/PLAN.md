# Plan 00001: Proof of Concept - Establish Wrapper Development Pattern

**Status**: Not Started
**Created**: 2026-02-17
**Owner**: TBD
**Priority**: High
**Recommended Executor**: Opus 4.6
**Execution Strategy**: Single-Threaded

## Overview

Before building wrappers for every language and tool, we need to establish and validate the end-to-end development pattern. This plan covers installing tooling, building one reference wrapper, creating acceptance test infrastructure, and documenting the repeatable process that subsequent language plans will follow.

The key challenge is: how do we verify that a wrapper actually works correctly? We need example codebases with known QA failures, a test harness that validates terminal output format, JSON schema compliance, and exit codes. This plan figures all of that out with a single tool (ESLint as the reference implementation) before we scale to dozens of tools across multiple languages.

## Goals

- Establish a repeatable, tested pattern for building wrappers
- Create acceptance test infrastructure that validates wrapper correctness
- Build one complete reference wrapper (ESLint) as the template
- Create example codebases with known pass/fail scenarios for testing
- Document the process so subsequent language plans are straightforward

## Non-Goals

- Building all wrappers (that's for Plans 00002-00005)
- CI/CD pipeline setup (premature at this stage)
- Publishing to package registries
- Supporting legacy tool versions

## Context & Background

The project has comprehensive documentation (MISSION.md, CONTRIBUTING.md) defining the wrapper contract:
- Terse terminal output: 1 line pass, 2-5 lines fail
- JSON output to temp file matching a schema
- Exit codes: 0=pass, 1=fail, 2=error
- Naming: `llm-{toolname}.{ext}`
- Wrappers in native language of the tool

What's missing is the practical implementation and, critically, the testing infrastructure to verify wrappers work correctly.

## Tasks

### Phase 1: Environment & Tooling Setup

- [ ] ⬜ **Task 1.1**: Install Node.js 20+ and verify availability
  - [ ] ⬜ Confirm `node --version` and `npm --version`
- [ ] ⬜ **Task 1.2**: Install PHP 8.2+ and Composer and verify availability
  - [ ] ⬜ Confirm `php --version` and `composer --version`
- [ ] ⬜ **Task 1.3**: Verify Python 3.11+ is available (already present for hooks daemon)
- [ ] ⬜ **Task 1.4**: Install Bash testing tools (shellcheck, bats-core or similar)

### Phase 2: Test Fixture Codebases

- [ ] ⬜ **Task 2.1**: Create `test-fixtures/` directory structure
  - [ ] ⬜ `test-fixtures/nodejs/eslint/pass/` - Clean code that passes ESLint
  - [ ] ⬜ `test-fixtures/nodejs/eslint/fail/` - Code with known ESLint violations
- [ ] ⬜ **Task 2.2**: Design fixture conventions and document them
  - [ ] ⬜ Each fixture should have a `README.md` explaining what it tests
  - [ ] ⬜ Fail fixtures should document expected error counts/types

### Phase 3: Acceptance Test Framework

- [ ] ⬜ **Task 3.1**: Design the acceptance test approach
  - [ ] ⬜ Decide on test runner (language-native tests, or a cross-language harness?)
  - [ ] ⬜ Define what "acceptance" means for a wrapper:
    - Terminal output matches expected format (regex validation)
    - JSON output validates against schema.json
    - Exit code is correct (0 for pass fixture, 1 for fail fixture)
    - JSON contains expected error counts for fail fixtures
- [ ] ⬜ **Task 3.2**: Build the acceptance test harness
  - [ ] ⬜ Script that runs a wrapper against pass/fail fixtures
  - [ ] ⬜ Validates terminal output format
  - [ ] ⬜ Validates JSON against schema using a JSON schema validator
  - [ ] ⬜ Validates exit codes
  - [ ] ⬜ Reports pass/fail per check
- [ ] ⬜ **Task 3.3**: Consider cross-language test runner
  - [ ] ⬜ Since wrappers are in different languages, the test harness itself should probably be language-agnostic
  - [ ] ⬜ Python is a good candidate (json schema validation libraries, subprocess for running wrappers)

### Phase 4: Reference Implementation (ESLint Wrapper)

- [ ] ⬜ **Task 4.1**: Create wrapper directory structure
  - [ ] ⬜ `wrappers/nodejs/eslint/` with all required files
- [ ] ⬜ **Task 4.2**: Build `llm-eslint.js`
  - [ ] ⬜ Run ESLint programmatically (not CLI subprocess)
  - [ ] ⬜ Format terse terminal output per spec
  - [ ] ⬜ Write JSON to temp file
  - [ ] ⬜ Set correct exit codes
- [ ] ⬜ **Task 4.3**: Define `schema.json` for ESLint output
- [ ] ⬜ **Task 4.4**: Create `examples/pass.json` and `examples/fail.json`
- [ ] ⬜ **Task 4.5**: Write `README.md` for the wrapper
- [ ] ⬜ **Task 4.6**: Create `package.json` with dependencies and engine requirements

### Phase 5: Validate & Iterate

- [ ] ⬜ **Task 5.1**: Run acceptance tests against ESLint wrapper
  - [ ] ⬜ Test against pass fixture - verify exit 0, terse output, valid JSON
  - [ ] ⬜ Test against fail fixture - verify exit 1, terse output, valid JSON, correct error counts
- [ ] ⬜ **Task 5.2**: Test edge cases
  - [ ] ⬜ Missing ESLint config - should exit 2
  - [ ] ⬜ Invalid target path - should exit 2
  - [ ] ⬜ Empty project (no files to lint) - should exit 0
- [ ] ⬜ **Task 5.3**: Verify jq queries work as documented
  - [ ] ⬜ `jq '.summary.error_count'` on output
  - [ ] ⬜ `jq '.results[] | select(.errors | length > 0)'` on output

### Phase 6: Document the Pattern

- [ ] ⬜ **Task 6.1**: Write a `WRAPPER_DEVELOPMENT_GUIDE.md` capturing lessons learned
  - [ ] ⬜ Step-by-step process for adding a new wrapper
  - [ ] ⬜ How to create test fixtures
  - [ ] ⬜ How to run acceptance tests
  - [ ] ⬜ Common pitfalls and solutions
- [ ] ⬜ **Task 6.2**: Update CONTRIBUTING.md if any conventions changed during PoC

## Technical Decisions

### Decision 1: Acceptance Test Language
**Context**: Wrappers are in multiple languages, but we need a single test harness.
**Options Considered**:
1. Python - good JSON schema validation libraries, subprocess handling, already available
2. Node.js - could use Jest, but biases toward one language
3. Bash/BATS - language-agnostic but JSON handling is painful (contradicts our own principles)
**Decision**: TBD during Phase 3 - leaning toward Python for cross-language testing
**Date**: 2026-02-17

### Decision 2: Programmatic vs CLI Invocation
**Context**: Wrappers can invoke tools programmatically (as a library) or shell out to the CLI.
**Options Considered**:
1. Programmatic (import the tool's API) - better error handling, structured data natively
2. CLI subprocess + parse output - simpler but fragile
**Decision**: TBD - likely tool-dependent. ESLint has good programmatic API; some tools may not.
**Date**: 2026-02-17

## Success Criteria

- [ ] One complete wrapper (ESLint) passes all acceptance tests
- [ ] Acceptance test harness can be reused for any future wrapper
- [ ] Test fixtures exist with known pass/fail scenarios
- [ ] The pattern is documented well enough that Plans 00002-00005 can follow it mechanically
- [ ] jq queries demonstrated working against real output

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tool APIs change between versions | Medium | Low | Pin minimum versions, test against specific versions |
| JSON schema validation tooling varies across languages | Medium | Medium | Use a single Python-based validator for all wrappers |
| Test fixtures become stale as tools update rules | Low | Medium | Keep fixtures minimal with stable, well-known violations |
| Programmatic API not available for some tools | Medium | Medium | Allow CLI-based wrappers as fallback, document when and why |

## Notes & Updates

### 2026-02-17
- Plan created as prerequisite to all language-specific plans
- ESLint chosen as reference implementation due to mature programmatic API
