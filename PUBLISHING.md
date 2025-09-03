# PyPI Publishing Guide for fdprof

This guide explains how to publish fdprof to PyPI using the automated GitHub Actions workflow.

## Overview

The project is configured with automated PyPI publishing that triggers when you create a new GitHub release. The workflow:

1. ✅ **Builds** the wheel and source distribution
2. ✅ **Tests** installation across multiple platforms (Windows, macOS, Linux)
3. ✅ **Validates** that the release tag matches the package version
4. ✅ **Publishes** to PyPI automatically using trusted publishing
5. ✅ **Uploads** build artifacts to the GitHub release

## Prerequisites

### 1. Set Up PyPI Trusted Publishing (Required)

You must configure trusted publishing on PyPI **before** your first release:

1. **Create a PyPI account** at https://pypi.org/account/register/ if you don't have one
2. **Add the fdprof project** to PyPI:
   - Go to https://pypi.org/manage/account/publishing/
   - Click "Add a new pending publisher"
   - Fill in the form:
     - **PyPI project name**: `fdprof`
     - **Owner**: `ianhi`
     - **Repository name**: `fdprof`
     - **Workflow filename**: `publish.yml`
     - **Environment name**: `pypi`

3. **For TestPyPI** (optional, for pre-releases):
   - Go to https://test.pypi.org/manage/account/publishing/
   - Repeat the same process with environment name `testpypi`

### 2. Version Management

The workflow validates that your release tag matches the version in `pyproject.toml`:

- **Version in pyproject.toml**: `version = "0.1.0"`
- **Release tag**: Should be `v0.1.0` or `0.1.0`

## Release Process

### Step 1: Update Version

Update the version in `pyproject.toml`:

```toml
[project]
name = "fdprof"
version = "0.2.0"  # Update this
```

### Step 2: Commit and Push Changes

```bash
git add pyproject.toml
git commit -m "Bump version to 0.2.0"
git push origin main
```

### Step 3: Create a GitHub Release

**Option A: Using GitHub Web Interface**

1. Go to https://github.com/ianhi/fdprof/releases
2. Click "Create a new release"
3. **Tag**: `v0.2.0` (must match version in pyproject.toml)
4. **Title**: `Release v0.2.0`
5. **Description**: Add release notes describing changes
6. For pre-releases: Check "This is a pre-release"
7. Click "Publish release"

**Option B: Using GitHub CLI**

```bash
# Regular release
gh release create v0.2.0 \
    --title "Release v0.2.0" \
    --notes "Release notes here"

# Pre-release (publishes to TestPyPI instead)
gh release create v0.2.0-rc1 \
    --title "Release v0.2.0-rc1" \
    --notes "Release candidate" \
    --prerelease
```

### Step 4: Monitor the Workflow

1. Go to https://github.com/ianhi/fdprof/actions
2. Watch the "Publish to PyPI" workflow run
3. The workflow will:
   - ✅ Build the package
   - ✅ Test installation on multiple platforms
   - ✅ Publish to PyPI (or TestPyPI for pre-releases)
   - ✅ Upload files to the GitHub release

## Workflow Details

### Jobs Breakdown

1. **`build`**: Creates wheel and source distribution
2. **`test-install`**: Tests installation on Windows/macOS/Linux with Python 3.8-3.12
3. **`publish-to-pypi`**: Publishes to PyPI (production releases only)
4. **`publish-to-testpypi`**: Publishes to TestPyPI (pre-releases only)
5. **`create-github-release-assets`**: Uploads build artifacts to GitHub release

### Version Validation

The workflow automatically validates that your release tag matches the package version:

```bash
# ✅ These match - workflow succeeds
Release tag: v0.2.0
Package version: 0.2.0

# ❌ These don't match - workflow fails
Release tag: v0.2.1
Package version: 0.2.0
```

### Environment Protection

The workflow uses GitHub environments for security:
- **`pypi`**: For production PyPI publishing
- **`testpypi`**: For TestPyPI pre-release publishing

## Troubleshooting

### Common Issues

**1. "Version mismatch" error**
```
❌ Version mismatch: tag=0.2.0, package=0.1.0
```
**Fix**: Update `version = "0.2.0"` in `pyproject.toml` to match your release tag.

**2. "Trusted publishing not configured" error**
```
❌ HTTPError: 403 Forbidden
```
**Fix**: Set up trusted publishing on PyPI as described in Prerequisites.

**3. "Package already exists" error**
```
❌ HTTPError: 400 Bad Request (File already exists)
```
**Fix**: You cannot republish the same version. Increment the version number.

### Testing Before Release

**Test the build locally:**
```bash
# Clean build
rm -rf dist/
uv build

# Test wheel installation
pip install dist/*.whl
fdprof --help
```

**Test with TestPyPI (pre-release):**
```bash
# Create pre-release
gh release create v0.2.0-rc1 --prerelease --notes "Release candidate"

# Install from TestPyPI after workflow completes
pip install --index-url https://test.pypi.org/simple/ fdprof==0.2.0rc1
```

## Security Notes

- ✅ **No API tokens needed** - Uses OpenID Connect trusted publishing
- ✅ **Minimal permissions** - Workflow only has read access to repository
- ✅ **Environment protection** - Requires review for sensitive operations
- ✅ **Version validation** - Prevents accidental releases

## Local Publishing (Alternative)

If you prefer to publish manually from your laptop instead of using GitHub Actions:

### Prerequisites for Local Publishing

1. **Install publishing tools:**
   ```bash
   uv add --dev twine
   # or with pip: pip install twine
   ```

2. **Set up PyPI API token:**
   - Go to https://pypi.org/manage/account/token/
   - Create a new API token with scope "Entire account"
   - Create `~/.pypirc`:
     ```ini
     [pypi]
     username = __token__
     password = pypi-your-token-here

     [testpypi]
     repository = https://test.pypi.org/legacy/
     username = __token__
     password = pypi-your-testpypi-token-here
     ```

### Local Publishing Steps

1. **Clean and build:**
   ```bash
   rm -rf dist/
   uv build
   ```

2. **Verify the build:**
   ```bash
   ls -la dist/
   # Should show: fdprof-X.Y.Z-py3-none-any.whl and fdprof-X.Y.Z.tar.gz

   # Test wheel contents
   unzip -l dist/*.whl
   ```

3. **Test upload to TestPyPI first:**
   ```bash
   uv run twine upload --repository testpypi dist/*

   # Test installation from TestPyPI
   pip install --index-url https://test.pypi.org/simple/ fdprof
   fdprof --help
   ```

4. **Upload to production PyPI:**
   ```bash
   uv run twine upload dist/*

   # Test installation from PyPI
   pip install fdprof
   fdprof --help
   ```

### Local Publishing Commands Reference

```bash
# Full local release workflow
rm -rf dist/                              # Clean previous builds
uv build                                  # Build wheel and source dist
uv run twine check dist/*                 # Validate packages
uv run twine upload --repository testpypi dist/*  # Test upload
uv run twine upload dist/*                # Production upload
```

### Advantages of Each Approach

**GitHub Actions (Recommended):**
- ✅ **Automated** - No manual steps
- ✅ **Tested** - Validates installation on multiple platforms
- ✅ **Secure** - No API tokens needed (trusted publishing)
- ✅ **Consistent** - Same process every time
- ✅ **Traceable** - Full audit trail in GitHub Actions

**Local Publishing:**
- ✅ **Immediate** - No waiting for workflows
- ✅ **Control** - Full control over timing
- ✅ **Offline-friendly** - Can work without GitHub
- ❌ **Manual** - More steps to remember
- ❌ **API tokens** - Need to manage credentials

## Next Steps After Setup

### Option 1: GitHub Actions (Recommended)
1. **Complete PyPI trusted publishing setup** (one-time)
2. **Test with a pre-release** first: `v0.1.0-rc1`
3. **Create your first production release**: `v0.1.0`
4. **Monitor the workflow** to ensure everything works

### Option 2: Local Publishing
1. **Set up PyPI API tokens** (one-time)
2. **Test local build and upload** to TestPyPI
3. **Publish to production PyPI**

Both methods will get fdprof published to PyPI! 🎉
