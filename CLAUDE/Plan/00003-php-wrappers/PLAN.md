# Plan 00003: PHP Tool Wrappers

**Status**: Not Started
**Created**: 2026-02-17
**Owner**: TBD
**Priority**: High
**Recommended Executor**: Sonnet 4.5
**Execution Strategy**: Sub-Agent Orchestration
**Blocked By**: Plan 00001 (Proof of Concept)

## Overview

Implement all PHP QA tool wrappers following the pattern established in Plan 00001. Each wrapper follows the `llm-{toolname}.php` convention, produces terse terminal output and detailed JSON logs, and is tested against pass/fail fixtures.

PHP is a Phase 1 language alongside Node.js, as stated in MISSION.md.

## Goals

- Implement wrappers for all major PHP QA tools
- Create test fixtures for each tool
- Pass acceptance tests for every wrapper
- Ensure Composer-based dependency management with PHP >= 8.2

## Non-Goals

- Supporting PHP < 8.2
- Wrapping framework-specific tools (Laravel Pint is a maybe)
- IDE integration plugins

## Context & Background

PHP QA tools generally support JSON output via CLI flags, which simplifies wrapper implementation. However, some tools (like PHP-CS-Fixer) have more complex output formats. Composer manages dependencies, and each wrapper will have its own `composer.json`.

## Tools to Wrap

| Tool | Category | JSON Output? | Priority |
|------|----------|--------------|----------|
| PHPStan | Static analysis | Yes (--error-format=json) | High |
| PHP-CS-Fixer | Code style | Yes (--format=json) | High |
| PHPUnit | Testing | Yes (--log-junit, custom) | High |
| Psalm | Static analysis | Yes (--output-format=json) | Medium |
| PHP_CodeSniffer | Code style | Yes (--report=json) | Medium |
| Rector | Refactoring/upgrades | Partial | Low |

## Tasks

### Phase 1: High-Priority Tools

- [ ] ⬜ **Task 1.1**: PHPStan wrapper (`llm-phpstan.php`)
  - [ ] ⬜ Create `wrappers/php/phpstan/` directory structure
  - [ ] ⬜ Build wrapper using PHPStan's `--error-format=json` output
  - [ ] ⬜ Define schema.json for static analysis results
  - [ ] ⬜ Create test fixtures (clean code, code with type errors / undefined methods)
  - [ ] ⬜ Create examples/pass.json and examples/fail.json
  - [ ] ⬜ Create composer.json with phpstan dependency and PHP >= 8.2
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.2**: PHP-CS-Fixer wrapper (`llm-php-cs-fixer.php`)
  - [ ] ⬜ Create `wrappers/php/php-cs-fixer/` directory structure
  - [ ] ⬜ Build wrapper using dry-run + JSON output
  - [ ] ⬜ Define schema.json for style violation results
  - [ ] ⬜ Create test fixtures (well-formatted code, poorly-formatted code)
  - [ ] ⬜ Run acceptance tests

- [ ] ⬜ **Task 1.3**: PHPUnit wrapper (`llm-phpunit.php`)
  - [ ] ⬜ Create `wrappers/php/phpunit/` directory structure
  - [ ] ⬜ Build wrapper capturing test results
  - [ ] ⬜ Define schema.json for test results (suites, assertions, failures)
  - [ ] ⬜ Create test fixtures (passing tests, failing tests)
  - [ ] ⬜ Run acceptance tests

### Phase 2: Medium-Priority Tools

- [ ] ⬜ **Task 2.1**: Psalm wrapper (`llm-psalm.php`)
  - [ ] ⬜ Similar to PHPStan but Psalm-specific output format
  - [ ] ⬜ May share some schema patterns with PHPStan

- [ ] ⬜ **Task 2.2**: PHP_CodeSniffer wrapper (`llm-phpcs.php`)
  - [ ] ⬜ Uses `--report=json` for structured output
  - [ ] ⬜ Different violation categories from PHP-CS-Fixer

### Phase 3: Integration & Validation

- [ ] ⬜ **Task 3.1**: Run full acceptance test suite across all PHP wrappers
- [ ] ⬜ **Task 3.2**: Verify Composer install works cleanly for each wrapper
- [ ] ⬜ **Task 3.3**: Test with realistic PHP projects (not just trivial fixtures)

## Success Criteria

- [ ] All high-priority wrappers pass acceptance tests
- [ ] Each wrapper has composer.json requiring PHP >= 8.2
- [ ] Terminal output matches spec
- [ ] Exit codes correct for all scenarios
- [ ] Composer dependencies install cleanly

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| PHPUnit JSON output requires custom listener | Medium | Medium | Use built-in --log-junit and transform, or use event system in PHPUnit 10+ |
| PHP-CS-Fixer dry-run output format varies | Low | Low | Pin minimum version, test against it |
| Composer autoload conflicts between wrappers | Medium | Low | Each wrapper has isolated composer.json |

## Notes & Updates

### 2026-02-17
- Plan created; blocked by Plan 00001 proof of concept
- PHP tools generally have better CLI JSON output than Node.js tools
- PHPStan and PHP-CS-Fixer are the most commonly used in modern PHP projects
