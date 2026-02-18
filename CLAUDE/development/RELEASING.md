# Release Process

## Overview

This project uses semantic versioning with `0.x.y` releases during initial development.
All releases MUST use the `/release` skill or follow this document exactly.

## Version Scheme

During initial development (pre-1.0):
- **0.MINOR.PATCH** (e.g., 0.1.0, 0.2.0, 0.2.1)
- MINOR bumps for new wrappers or significant changes
- PATCH bumps for fixes to existing wrappers

Post-1.0 (future):
- Standard semver: MAJOR.MINOR.PATCH

## Version Files

Version is recorded in ONE place:
- `package.json` → `"version": "X.Y.Z"` (root level)

## Release Steps

### Step 1: Pre-Release Validation

ALL must pass before proceeding:

1. **Clean git state**: `git status` shows no uncommitted changes
2. **All acceptance tests pass**: Run for every wrapper:
   ```bash
   python3 acceptance-tests/run_acceptance.py wrappers/{lang}/{tool} test-fixtures/{lang}/{tool}
   ```
3. **No existing tag**: `git tag -l vX.Y.Z` returns nothing
4. **GitHub CLI authenticated**: `gh auth status` passes

**If ANY check fails: STOP. Fix the issue first.**

### Step 2: Determine Version

Scan commits since last tag:
- New wrappers added → MINOR bump (0.1.0 → 0.2.0)
- Fixes to existing wrappers → PATCH bump (0.1.0 → 0.1.1)
- Breaking schema changes → MINOR bump (pre-1.0, breaking changes don't bump MAJOR)

### Step 3: Update Version

Update `package.json` version field.

### Step 4: Update CHANGELOG.md

Follow [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New wrappers, features

### Changed
- Modified wrappers, schema changes

### Fixed
- Bug fixes
```

Categorise commits since last tag. Filter out internal/test commits.

### Step 5: Create Release Notes

Create `RELEASES/vX.Y.Z.md` with:

```markdown
# vX.Y.Z - [Title]

**Release Date**: YYYY-MM-DD

## Summary

[2-3 sentence overview]

## Highlights

- Highlight 1
- Highlight 2

## Wrappers

| Language | Tool | Status |
|----------|------|--------|
| Node.js | ESLint | Available |
| ... | ... | ... |

## Changes

[Copy from CHANGELOG.md for this version]

## Installation

Clone and install wrapper dependencies:
\`\`\`bash
git clone https://github.com/edmondscommerce/llm-friendly-qa-wrappers.git
cd llm-friendly-qa-wrappers
# Install per-wrapper deps as needed
cd wrappers/nodejs/eslint && npm install
\`\`\`
```

### Step 6: Commit Release

```bash
git add package.json CHANGELOG.md RELEASES/vX.Y.Z.md
git commit -m "Release vX.Y.Z: [Title]"
```

### Step 7: Tag and Push

```bash
git tag -a vX.Y.Z -m "Release vX.Y.Z: [Title]"
git push origin main
git push origin vX.Y.Z
```

### Step 8: Create GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z - [Title]" \
  --notes-file RELEASES/vX.Y.Z.md \
  --latest
```

### Step 9: Post-Release Verification

- [ ] Tag exists on GitHub
- [ ] GitHub release is published and marked "Latest"
- [ ] Release notes render correctly

## Rules

- **Never** create tags manually outside this process
- **Never** edit CHANGELOG.md outside a release
- **Always** run acceptance tests before releasing
- **Always** use annotated tags (not lightweight)
- Releases are atomic: all steps complete or none do
