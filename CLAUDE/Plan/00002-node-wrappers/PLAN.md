# Plan 00002: Node.js Tool Wrappers

**Status**: Not Started
**Created**: 2026-02-17
**Owner**: TBD
**Priority**: High
**Recommended Executor**: Sonnet 4.5
**Execution Strategy**: Sub-Agent Orchestration
**Blocked By**: Plan 00001 (Proof of Concept)

## Overview

Implement all Node.js QA tool wrappers following the pattern established in Plan 00001. Each wrapper follows the `llm-{toolname}.js` convention, produces terse terminal output and detailed JSON logs, and is tested against pass/fail fixtures using the acceptance test harness.

Node.js is the highest priority language alongside PHP, as stated in MISSION.md Phase 1.

## Goals

- Implement wrappers for all major Node.js QA tools
- Create test fixtures for each tool
- Pass acceptance tests for every wrapper
- Ensure all wrappers are jq-queryable

## Non-Goals

- Supporting CommonJS-only environments (ESM preferred)
- Wrapping build tools (webpack, vite) - QA tools only
- Supporting Node.js < 20

## Context & Background

Node.js has a rich ecosystem of QA tools. Most have well-documented programmatic APIs, making them good candidates for native wrappers. The pattern from Plan 00001 (ESLint reference implementation) will be replicated for each tool.

## Tools to Wrap

| Tool | Category | Programmatic API? | Priority |
|------|----------|-------------------|----------|
| ESLint | Linting | Yes (ESLint class) | Done in PoC |
| Prettier | Formatting | Yes (prettier.check) | High |
| Jest | Testing | Yes (jest-cli) | High |
| TypeScript (tsc) | Type checking | Yes (ts.createProgram) | High |
| Vitest | Testing | Yes (vitest API) | Medium |
| Biome | Lint + Format | Yes (CLI with JSON output) | Medium |

## Tasks

### Phase 1: Replicate ESLint Pattern for Remaining High-Priority Tools

- [ ] ⬜ **Task 1.1**: Prettier wrapper (`llm-prettier.js`)
  - [ ] ⬜ Create `wrappers/nodejs/prettier/` directory structure
  - [ ] ⬜ Build wrapper using Prettier's `check()` API
  - [ ] ⬜ Define schema.json for formatting check results
  - [ ] ⬜ Create test fixtures (formatted vs unformatted code)
  - [ ] ⬜ Create examples/pass.json and examples/fail.json
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.2**: Jest wrapper (`llm-jest.js`)
  - [ ] ⬜ Create `wrappers/nodejs/jest/` directory structure
  - [ ] ⬜ Build wrapper using jest-cli programmatic API
  - [ ] ⬜ Define schema.json for test results (suites, tests, pass/fail/skip counts)
  - [ ] ⬜ Create test fixtures (passing tests, failing tests, mixed)
  - [ ] ⬜ Create examples/pass.json and examples/fail.json
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.3**: TypeScript wrapper (`llm-tsc.js`)
  - [ ] ⬜ Create `wrappers/nodejs/typescript/` directory structure
  - [ ] ⬜ Build wrapper using TypeScript compiler API
  - [ ] ⬜ Define schema.json for type errors (code, message, location)
  - [ ] ⬜ Create test fixtures (valid TS, TS with type errors)
  - [ ] ⬜ Create examples/pass.json and examples/fail.json
  - [ ] ⬜ Run acceptance tests

### Phase 2: Medium-Priority Tools

- [ ] ⬜ **Task 2.1**: Vitest wrapper (`llm-vitest.js`)
  - [ ] ⬜ Same structure as Jest but using Vitest API
  - [ ] ⬜ Schema may differ from Jest (Vitest has different result structure)

- [ ] ⬜ **Task 2.2**: Biome wrapper (`llm-biome.js`)
  - [ ] ⬜ Biome outputs JSON natively via CLI flags
  - [ ] ⬜ Wrapper may be simpler (transform Biome JSON to our schema)

### Phase 3: Integration & Validation

- [ ] ⬜ **Task 3.1**: Run full acceptance test suite across all Node.js wrappers
- [ ] ⬜ **Task 3.2**: Verify all schemas are jq-friendly with documented queries
- [ ] ⬜ **Task 3.3**: Update top-level README with Node.js wrapper inventory

## Success Criteria

- [ ] All high-priority wrappers pass acceptance tests
- [ ] Each wrapper has schema.json, examples, README, and test fixtures
- [ ] Terminal output matches spec (1 line pass, 2-5 lines fail)
- [ ] Exit codes correct for all scenarios (0, 1, 2)
- [ ] jq example queries documented and working

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Jest programmatic API is complex | Medium | Medium | Fall back to CLI with --json flag |
| TypeScript compiler API is verbose | Low | High | Focus on essential error info only |
| Tool version differences change output | Medium | Low | Pin minimum versions, test against them |

## Notes & Updates

### 2026-02-17
- Plan created; blocked by Plan 00001 proof of concept
- ESLint will already be done as part of PoC
- Tool list may expand based on community feedback
