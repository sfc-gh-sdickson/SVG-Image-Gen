# TODOs for Codebase Quality and Conformance

This file tracks actionable TODOs in the codebase. Each TODO is linked to a unique UUID and references the exact code location. Please check off items as you address them.

---

## Unused `type: ignore` Comments

- [ ] **UUID: 0e1e7b2a** — Remove unused type: ignore
  - Location: `src/svg_image_generator/__init__.py:12`
  - Context: `from .app import main  # type: ignore  # TODO[0e1e7b2a]: Remove unused type: ignore (see TODO.md)`

- [ ] **UUID: 1a2c3d4e** — Remove unused type: ignore
  - Location: `src/svg_image_generator/__init__.py:17`
  - Context: `from .services.ai_service import AIGenerationService  # type: ignore  # TODO[1a2c3d4e]: Remove unused type: ignore (see TODO.md)`

- [ ] **UUID: 2b3c4d5e** — Remove unused type: ignore
  - Location: `src/svg_image_generator/__init__.py:18`
  - Context: `from .services.session_service import SessionService  # type: ignore  # TODO[2b3c4d5e]: Remove unused type: ignore (see TODO.md)`

- [ ] **UUID: 3c4d5e6f** — Remove unused type: ignore
  - Location: `src/svg_image_generator/__init__.py:19`
  - Context: `from .services.storage_service import StorageService  # type: ignore  # TODO[3c4d5e6f]: Remove unused type: ignore (see TODO.md)`

---

## Missing Type Annotations in Tests

- [ ] **UUID: 6f7a8b9c** — Add type annotations
  - Location: `tests/test_authentication.py:34`
  - Context: `def test_get_active_session_fails_outside_snowflake(self):  # TODO[6f7a8b9c]: Add type annotations (see TODO.md)`

- [ ] **UUID: 7a8b9c0d** — Add type annotations
  - Location: `tests/test_authentication.py:41`
  - Context: `def test_snowflake_environment_session(self, mock_get_active_session):  # TODO[7a8b9c0d]: Add type annotations (see TODO.md)`

- [ ] **UUID: 8b9c0d1e** — Add type annotations
  - Location: `tests/test_authentication.py:54`
  - Context: `def test_local_environment_session_with_env_vars(self, mock_session_builder, mock_get_active_session):  # TODO[8b9c0d1e]: Add type annotations (see TODO.md)`

- [ ] **UUID: 9c0d1e2f** — Add type annotations
  - Location: `tests/test_authentication.py:96`
  - Context: `def test_local_environment_missing_env_vars(self, mock_get_active_session):  # TODO[9c0d1e2f]: Add type annotations (see TODO.md)`

- [ ] **UUID: a0b1c2d3** — Add type annotations
  - Location: `tests/test_authentication.py:118`
  - Context: `def test_environment_variable_validation(self):  # TODO[a0b1c2d3]: Add type annotations (see TODO.md)`

- [ ] **UUID: b1c2d3e4** — Add type annotations
  - Location: `tests/test_authentication.py:149`
  - Context: `def test_session_configuration_with_all_params(self, mock_session_builder):  # TODO[b1c2d3e4]: Add type annotations (see TODO.md)`

- [ ] **UUID: c2d3e4f5** — Add type annotations
  - Location: `tests/test_authentication.py:174`
  - Context: `def test_session_configuration_minimal_params(self, mock_session_builder):  # TODO[c2d3e4f5]: Add type annotations (see TODO.md)`

- [ ] **UUID: d3e4f506** — Add type annotations
  - Location: `tests/test_authentication.py:199`
  - Context: `def test_required_environment_variables(self):  # TODO[d3e4f506]: Add type annotations (see TODO.md)`

- [ ] **UUID: e4f50617** — Add type annotations
  - Location: `tests/test_authentication.py:209`
  - Context: `def validate_env_vars():  # TODO[e4f50617]: Add type annotations (see TODO.md)`

- [ ] **UUID: f5061728** — Add type annotations
  - Location: `tests/test_authentication.py:231`
  - Context: `def test_optional_environment_variables(self):  # TODO[f5061728]: Add type annotations (see TODO.md)`

---

## General TODOs

- [ ] Re-enable and pass all pre-commit hooks (ruff, flake8, mypy, bandit, prettier)
- [ ] Fix all line length violations (E501) and other style issues flagged by ruff/flake8
- [ ] Address all security warnings flagged by bandit (e.g., SQL injection, subprocess usage)
- [ ] Upgrade Node.js to v14+ and re-enable Prettier
- [ ] Update documentation and ontology files as needed

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
