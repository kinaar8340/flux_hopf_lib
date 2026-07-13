# Publishing flux-hopf-lib

## Trusted Publishing (no API tokens in the repo)

Configured on:

| Index | Project name | Environment | Workflow |
|-------|--------------|-------------|----------|
| [TestPyPI](https://test.pypi.org/) | `flux-hopf-lib` | `testpypi` | `publish.yml` |
| [PyPI](https://pypi.org/) | `flux-hopf-lib` | `pypi` | `publish.yml` |

GitHub repo: `kinaar8340/flux_hopf_lib`  
Pending publishers claim the project name on the **first successful OIDC upload**.

## Workflows

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Tests + build check on every PR / push to `main` |
| `.github/workflows/publish.yml` | Build + Trusted Publish on tags / manual dispatch |

### Tag rules

| Tag example | Publishes to |
|-------------|--------------|
| `v0.1.0-test` | **TestPyPI** only |
| `v0.1.0`, `v0.2.0` | **PyPI** only |

### Manual dispatch

GitHub → Actions → **Publish to PyPI** → Run workflow → choose `testpypi` or `pypi`.

## First-time TestPyPI (recommended)

1. Confirm pending publisher on  
   https://test.pypi.org/manage/account/publishing/  
   matches repo + `publish.yml` + environment **`testpypi`**.
2. Ensure GitHub environment **`testpypi`** exists  
   (Settings → Environments) with no extra required secrets for OIDC.
3. Trigger a TestPyPI publish (pick one):

```bash
# Option A — test tag (does not pollute real PyPI)
git tag v0.1.0-test
git push origin v0.1.0-test

# Option B — Actions UI: workflow_dispatch → target=testpypi
```

4. Verify:

```bash
pip install --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  flux-hopf-lib==0.1.0
python -c "import flux_hopf_lib; print(flux_hopf_lib.__version__)"
```

(`--extra-index-url` pulls numpy/scipy from real PyPI.)

## First-time real PyPI

1. Confirm pending publisher on  
   https://pypi.org/manage/account/publishing/  
   matches repo + `publish.yml` + environment **`pypi`**.
2. Ensure GitHub environment **`pypi`** exists.
3. Publish (after TestPyPI looks good):

```bash
# v0.1.0 already exists as a git tag — re-run workflow on that tag:
gh workflow run "Publish to PyPI" --ref v0.1.0 -f target=pypi

# Or push a new version after bumping pyproject + __init__:
# git tag v0.1.1 && git push origin v0.1.1
```

4. Install cleanly:

```bash
pip install flux-hopf-lib==0.1.0
```

5. Update consumers / HF Spaces from git pins to:

```text
flux-hopf-lib==0.1.0
```

## Future releases

1. Update `CHANGELOG.md` under `[Unreleased]` → new section.
2. Bump version in **both**:
   - `pyproject.toml` → `version = "0.2.0"`
   - `src/flux_hopf_lib/__init__.py` → `__version__ = "0.2.0"`
3. Commit, tag, push:

```bash
git commit -am "release: v0.2.0"
git tag -a v0.2.0 -m "flux-hopf-lib 0.2.0"
git push origin main --tags
```

4. Bump consumer pins / HF Space requirements to the new version.

## Semver discipline

| Change type | Version |
|-------------|---------|
| Docs, tests, bugfixes | `0.1.x` patch |
| New APIs, non-breaking | `0.x.0` minor |
| κ / R / PDE / Hopf convention breaks | `x.0.0` major (or clear minor with migration notes) |
