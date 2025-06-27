# 📦 Refactoring Plan: Remove `pyarrow`, Adopt `nanoarrow` via Snowpark

**Date:** 2025-06-27
**Author:** ChatGPT Deployment Assistant
**Goal:** Replace legacy `pyarrow` dependency with Snowpark-native DataFrame handling (`nanoarrow`), improve compatibility and reduce deployment overhead.

---

## 🎯 Objective

Remove `pyarrow` from the SVG Image Generator project, leveraging Snowflake Snowpark's built-in support for data movement using `nanoarrow`.

---

## ✅ Phase 1: Audit & Preparation

- Search for all `import pyarrow` usage.
- Check `requirements.txt`, `pyproject.toml`, and any lock files.
- Confirm `snowflake-snowpark-python >= 1.6.0`.

---

## 🔧 Phase 2: Replace with Snowpark-native APIs

- Refactor `pyarrow.Table.from_pandas(df)` to `session.table(...).to_pandas()`.
- Replace low-level Arrow code with native DataFrame methods in Snowpark.
- Create or update `data_io.py` to abstract read/write operations.

---

## 📦 Phase 3: Refactor Dependency Management

- Remove `pyarrow` from `requirements.txt`.
- Add `snowflake-snowpark-python[pandas] >= 1.6.0`.
- Optional: keep `pyarrow` in `requirements-dev.txt` for legacy test harnesses.

---

## 🧪 Phase 4: Validate and Test

- Replace Arrow-specific tests with Pandas-based checks.
- Run integration tests in both SiS and CLI environments.
- Snapshot test SVGs to confirm no semantic drift.

---

## 🔄 Phase 5: CI/CD and Deployment

- Add version check to CI for Snowpark and `pyarrow` absence.
- Test deployment in SiS (Streamlit in Snowflake).
- Confirm `.to_pandas()` works with no performance regressions.

---

## 📈 Phase 6: Documentation and Maintenance

- Update `README.md` to reflect `pyarrow` deprecation.
- Add versioned TTL entries to `system_model.ttl`:
  - Replaced `pyarrow` with `nanoarrow`
  - Justify decision in ontological metadata

---

## ✅ Deliverables

| Deliverable            | Path                             |
|------------------------|----------------------------------|
| `data_io.py`           | `/app/core/`                     |
| Updated requirements   | `/requirements.txt`, `/dev.txt` |
| TTL delta              | `/ontologies/system_model.ttl`   |
| Snapshot test results  | `/tests/`                        |
| CI check               | `.github/workflows/ci.yml`       |
| Doc update             | `/README.md`                     |
