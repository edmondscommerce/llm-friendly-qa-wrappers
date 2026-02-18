---
name: release
description: Create a new release of QA Tool Wrappers - runs acceptance tests, bumps version, generates changelog, tags, and publishes GitHub release
argument-hint: "[version]"
---

# Release QA Tool Wrappers

Create a new release following the documented release process.

## Usage

```bash
/release          # Auto-detect version bump from commits
/release 0.2.0    # Release specific version
```

## Process

Follow `@CLAUDE/development/RELEASING.md` exactly. The steps are:

1. **Validate** - Clean git, all acceptance tests pass, no existing tag
2. **Version** - Determine or use specified version
3. **Update** - Bump version in package.json
4. **Changelog** - Generate CHANGELOG.md entry from commits since last tag
5. **Release notes** - Create RELEASES/vX.Y.Z.md
6. **Commit** - Single release commit
7. **Tag** - Annotated git tag
8. **Push** - Push commit and tag
9. **Publish** - Create GitHub release via `gh release create`
10. **Verify** - Confirm release is live

## Implementation

Read and follow `@CLAUDE/development/RELEASING.md` for the complete release process.

### Step 1: Pre-Release Validation

```bash
# Clean git state
git status

# Run ALL acceptance tests
for wrapper_dir in wrappers/*/*; do
  tool=$(basename "$wrapper_dir")
  lang=$(basename "$(dirname "$wrapper_dir")")
  fixture_dir="test-fixtures/$lang/$tool"
  if [ -d "$fixture_dir" ]; then
    echo "Testing $lang/$tool..."
    python3 acceptance-tests/run_acceptance.py "$wrapper_dir" "$fixture_dir"
  fi
done

# Check no existing tag
git tag -l "v$VERSION"

# GitHub CLI auth
gh auth status
```

If any acceptance test fails, STOP and report the failure. Do not proceed.

### Step 2: Determine Version

If no version argument provided, scan commits since last tag:
```bash
# Get last tag
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

# Get commits since last tag (or all commits if no tag)
if [ -n "$LAST_TAG" ]; then
  git log "$LAST_TAG"..HEAD --oneline
else
  git log --oneline
fi
```

- New wrappers (directories added under wrappers/) → MINOR bump
- Fixes only → PATCH bump
- If first release, use 0.1.0

### Step 3: Update Files and Create Release

Follow Steps 3-9 from `@CLAUDE/development/RELEASING.md`:
- Update package.json version
- Generate CHANGELOG.md
- Create RELEASES/vX.Y.Z.md with wrapper inventory table
- Commit, tag, push, create GitHub release

### Wrapper Inventory

When creating release notes, generate a current inventory by scanning:
```bash
for wrapper_dir in wrappers/*/*; do
  tool=$(basename "$wrapper_dir")
  lang=$(basename "$(dirname "$wrapper_dir")")
  echo "| $lang | $tool |"
done
```
