# 🔄 Rollback Plan: PyArrow → NanoArrow Migration

## Objective
Provide a safe path to revert to PyArrow-based DataFrame transport if NanoArrow integration proves incompatible or unstable in any deployment context (e.g., SiS).

---

## Rollback Conditions

Rollback if any of the following occur:
- ❌ `.to_pandas()` or `.to_arrow()` fails without `pyarrow`
- ❌ Snowflake SiS does not support nanoarrow path
- ❌ Performance degrades by >20%
- ❌ Active session fails to resolve data correctly

---

## Rollback Steps

### 1. Reinstate pyarrow in requirements

In `requirements.txt` or `pyproject.toml`:
```toml
pyarrow<19.0.0
```

### 2. Re-enable pyarrow fallback in code
```python
try:
    import pyarrow as pa
    use_pyarrow = True
except ImportError:
    use_pyarrow = False
```

### 3. Disable NanoArrow-only optimizations
Wrap any nanoarrow-specific logic in:
```python
if not use_pyarrow:
    # safe nanoarrow path
```

### 4. Redeploy affected bundles
- Push updated package to SiS and PyPI
- Trigger fallback logging in CI/CD

---

## Recovery Timeline
Rollback can be completed in under 1 hour in all deployment environments.

---

## Status Flags

- [ ] `pyarrow` re-added
- [ ] Tests pass with fallback
- [ ] Deployment stable post-revert
