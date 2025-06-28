# TODO

## ✅ Completed

### Core Infrastructure
- [x] Runtime detection system for multiple environments
- [x] Three-tier authentication system (active session, connections.toml, env vars)
- [x] LLM-friendly structured logging system
- [x] Git integration with dynamic discovery (no hardcoded names)
- [x] Admin diagnostics dashboard with security warnings
- [x] SQL integration script with proper privilege management
- [x] Comprehensive test suite with PDCA framework integration
- [x] Business authority principles documentation
- [x] Ontology models and validation tests

### Git Integration
- [x] Dynamic integration discovery
- [x] Repository listing, file read/write, branch creation
- [x] State interrogation (always check state as precondition)
- [x] Error handling and logging
- [x] Runtime-aware operations

### Testing
- [x] Authentication tests with three-tier validation
- [x] Runtime detection tests for all environments
- [x] LLM logging tests with JSON serialization
- [x] Git integration tests with dynamic discovery
- [x] Ontology completeness and validation tests

### Documentation
- [x] Project architecture documentation
- [x] System components documentation
- [x] Business authority principles in README and CONTRIBUTING
- [x] Admin tool security documentation

## 🚧 In Progress

### Deployment Preparation
- [ ] Test admin diagnostics in Snowflake environment
- [ ] Validate runtime detection in actual Snowflake runtime
- [ ] Test Git integration with real Snowflake API integration
- [ ] Verify LLM logging in restricted environments

## 📋 Next Priorities

### Snowflake Deployment
- [ ] Deploy admin diagnostics to Snowflake workspace
- [ ] Test capability detection in real Snowflake environment
- [ ] Validate session management in Streamlit-in-Snowflake
- [ ] Test Git integration with actual Snowflake API integration
- [ ] Verify graceful degradation in restricted environments

### Main Application Enhancement
- [ ] Integrate runtime detection into main SVG-Image-Gen.py
- [ ] Add capability-aware feature availability
- [ ] Implement graceful degradation for restricted environments
- [ ] Add LLM logging to main application workflows
- [ ] Test main app in Snowflake environment

### Cursor Integration
- [ ] Research Cursor integration capabilities in Snowflake
- [ ] Determine if Cursor can be used within Snowflake workspace
- [ ] Explore Cursor API or extension possibilities
- [ ] Test Cursor functionality in restricted environments

### Production Readiness
- [ ] Complete end-to-end testing in Snowflake
- [ ] Validate all features work in production environment
- [ ] Test error handling and recovery in Snowflake
- [ ] Verify logging and monitoring in production
- [ ] Performance testing in Snowflake environment

### Documentation Updates
- [ ] Update deployment guides for Snowflake
- [ ] Document Cursor integration findings
- [ ] Create troubleshooting guides for common issues
- [ ] Update user documentation for production deployment

## 🔮 Future Enhancements

### Advanced Features
- [ ] Multi-branch deployment support
- [ ] Advanced Git workflow integration
- [ ] Enhanced error recovery mechanisms
- [ ] Performance optimization for Snowflake
- [ ] Advanced monitoring and alerting

### Integration Enhancements
- [ ] Additional external service integrations
- [ ] Enhanced API integration capabilities
- [ ] Advanced secret management
- [ ] Multi-environment deployment automation

### MDC2 Development
- [ ] Continue MDC2 strategy development
- [ ] Implement MDC2 parser and validator
- [ ] Create migration tools from MDC to MDC2
- [ ] Develop MDC2 ecosystem tools

## 🐛 Known Issues

### Test Coverage
- [ ] Improve test coverage to meet 75% requirement
- [ ] Add more integration tests for Snowflake environment
- [ ] Enhance error scenario testing
- [ ] Add performance testing

### Documentation
- [ ] Add more detailed deployment instructions
- [ ] Create troubleshooting guides
- [ ] Document environment-specific configurations
- [ ] Add user guides for admin tools

## 📝 Notes

- **Current Branch**: `feature/snowflake-deployment`
- **Target Environment**: Snowflake Native Apps
- **Key Principle**: Always interrogate state as precondition
- **Business Authority**: Platform safety ≠ Business authority
- **Testing Strategy**: Test-driven development with PDCA framework

# TODOs for Codebase Quality and Conformance

This file tracks actionable TODOs in the codebase. Each TODO is linked to a unique UUID and references the exact code location. Please check off items as you address them.

---

## Unused `type: ignore` Comments

- [x] ~~**UUID: 0e1e7b2a** — Remove unused type: ignore~~ ✅ **COMPLETED**
  - Location: `src/svg_image_generator/__init__.py:12`
  - Context: `from .app import main  # type: ignore  # TODO[0e1e7b2a]: Remove unused type: ignore (see TODO.md)`
  - **Status**: No `type: ignore` comments found in `src/svg_image_generator/__init__.py`

- [x] ~~**UUID: 1a2c3d4e** — Remove unused type: ignore~~ ✅ **COMPLETED**
  - Location: `src/svg_image_generator/__init__.py:17`
  - Context: `from .services.ai_service import AIGenerationService  # type: ignore  # TODO[1a2c3d4e]: Remove unused type: ignore (see TODO.md)`
  - **Status**: No `type: ignore` comments found in `src/svg_image_generator/__init__.py`

- [x] ~~**UUID: 2b3c4d5e** — Remove unused type: ignore~~ ✅ **COMPLETED**
  - Location: `src/svg_image_generator/__init__.py:18`
  - Context: `from .services.session_service import SessionService  # type: ignore  # TODO[2b3c4d5e]: Remove unused type: ignore (see TODO.md)`
  - **Status**: No `type: ignore` comments found in `src/svg_image_generator/__init__.py`

- [x] ~~**UUID: 3c4d5e6f** — Remove unused type: ignore~~ ✅ **COMPLETED**
  - Location: `src/svg_image_generator/__init__.py:19`
  - Context: `from .services.storage_service import StorageService  # type: ignore  # TODO[3c4d5e6f]: Remove unused type: ignore (see TODO.md)`
  - **Status**: No `type: ignore` comments found in `src/svg_image_generator/__init__.py`

---

## Missing Type Annotations in Tests

- [ ] **UUID: 6f7a8b9c** — Add type annotations
  - Location: `tests/test_authentication.py:34`
  - Context: `def test_get_active_session_fails_outside_snowflake(self):  # TODO[6f7a8b9c]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: 7a8b9c0d** — Add type annotations
  - Location: `tests/test_authentication.py:41`
  - Context: `def test_snowflake_environment_session(self, mock_get_active_session):  # TODO[7a8b9c0d]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: 8b9c0d1e** — Add type annotations
  - Location: `tests/test_authentication.py:54`
  - Context: `def test_local_environment_session_with_env_vars(self, mock_session_builder, mock_get_active_session):  # TODO[8b9c0d1e]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: 9c0d1e2f** — Add type annotations
  - Location: `tests/test_authentication.py:96`
  - Context: `def test_local_environment_missing_env_vars(self, mock_get_active_session):  # TODO[9c0d1e2f]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: a0b1c2d3** — Add type annotations
  - Location: `tests/test_authentication.py:118`
  - Context: `def test_environment_variable_validation(self):  # TODO[a0b1c2d3]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: b1c2d3e4** — Add type annotations
  - Location: `tests/test_authentication.py:149`
  - Context: `def test_session_configuration_with_all_params(self, mock_session_builder):  # TODO[b1c2d3e4]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: c2d3e4f5** — Add type annotations
  - Location: `tests/test_authentication.py:174`
  - Context: `def test_session_configuration_minimal_params(self, mock_session_builder):  # TODO[c2d3e4f5]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: d3e4f506** — Add type annotations
  - Location: `tests/test_authentication.py:199`
  - Context: `def test_required_environment_variables(self):  # TODO[d3e4f506]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: e4f50617** — Add type annotations
  - Location: `tests/test_authentication.py:209`
  - Context: `def validate_env_vars():  # TODO[e4f50617]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

- [ ] **UUID: f5061728** — Add type annotations
  - Location: `tests/test_authentication.py:231`
  - Context: `def test_optional_environment_variables(self):  # TODO[f5061728]: Add type annotations (see TODO.md)`
  - **Status**: Still missing type annotations

---

## General TODOs

- [ ] Re-enable and pass all pre-commit hooks (ruff, flake8, mypy, bandit, prettier)
  - **Status**: Found E501 (line length) violations in `src/svg_image_generator/__init__.py`
  - **Status**: Found B904 (exception chaining) violations in `src/svg_image_generator/cortex.py`

- [ ] Fix all line length violations (E501) and other style issues flagged by ruff/flake8
  - **Status**: Lines 5 and 17 in `src/svg_image_generator/__init__.py` exceed 88 characters

- [ ] Address all security warnings flagged by bandit (e.g., SQL injection, subprocess usage)
  - **Status**: Found B904 exception chaining issues in `src/svg_image_generator/cortex.py`

- [ ] Upgrade Node.js to v14+ and re-enable Prettier
  - **Status**: Not checked

- [ ] Update documentation and ontology files as needed
  - **Status**: Not checked

---


## Tooling Improvements

- [x] **UUID: tool-001** — Create TODO management tool (Initial version created: `scripts/todo_manager.py`)
  - **Priority: High**
  - **Context**: Current TODO management relies on manual file editing with `replace_in_file` or `write_to_file` tools, which is error-prone and doesn't provide proper TODO lifecycle management
  - **Requirements**:
    - Automated TODO creation with UUID generation
    - TODO status tracking (open, in-progress, completed)
    - Integration with code locations and context
    - Bulk operations for TODO management
    - Reporting and analytics on TODO completion
    - Integration with pre-commit hooks for TODO validation
  - **Alternative**: Consider existing tools like `todoist`, `taskwarrior`, or custom script
  - **Note**: This tool is critical for maintaining the systematic TODO approach outlined in this file

## TODO: Systemic Remediation for Snowflake Identifier Case Sensitivity and Semantic Assumptions

**Pattern:**
- All code that queries Snowflake (SQL strings, Snowpark DataFrame `.select()`, `.filter()`, etc.) must use **quoted, lowercase identifiers** for column names (e.g., `"name"` not `NAME`).
- Snowflake treats unquoted identifiers as uppercase, which will not match columns created as lowercase or quoted.
- Snowpark DataFrame operations may not quote identifiers, leading to subtle, environment-dependent bugs.

**Why:**
- This causes runtime errors that are hard to debug and may only appear in certain environments or with certain data.
- Example error: `SQL compilation error: invalid identifier 'NAME'. Do you mean '"name"'?`

**Action Items:**
- [ ] **Audit all SQL and DataFrame code** for unquoted identifiers.
- [ ] **Refactor** to use quoted identifiers everywhere:
    - SQL: `SELECT "name" FROM ...`
    - Snowpark: `.select('"name"')`, `.filter('"name" IS NOT NULL')`
- [ ] **Add regression tests** for identifier quoting/case-sensitivity.
- [ ] **Document this gotcha** in the README and onboarding docs.
- [ ] **Add code comments** in all places where this is relevant.
- [ ] **Consider a linter/static check** for unquoted identifiers in `.sql` and Python code.

**References:**
- https://docs.snowflake.com/en/sql-reference/identifiers-syntax

---

## Summary

**Completed Items:** 5/26 (19.2%)
- ✅ All 4 unused `type: ignore` comments have been removed
- ✅ TODO management tool created

**Remaining Items:** 21/26 (80.8%)
- ❌ 10 missing type annotations in tests
- ❌ 5 general TODOs (pre-commit hooks, line length, security, Node.js, docs)
- ❌ 6 Snowflake identifier case sensitivity items
