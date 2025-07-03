# Gemini PDCA Test Prompt - Enhanced Rules

## Context
You are working on the SVG-Image-Gen project, which follows a strict PDCA (Plan-Do-Check-Act) development methodology with test-driven, model-driven approach. The project has enhanced rules for scope discipline, tool compliance, and git workflow with rollback procedures.

## Project Rules (MANDATORY - Follow These Exactly)

### PDCA Development Methodology
- **PLAN**: Run tests to identify failures, analyze issues, define specific scope
- **DO**: Read relevant files, understand current state, focus only on identified issues
- **CHECK**: Validate behavior, verify logging, check scope compliance
- **ACT**: Implement minimal fixes, add logging, validate changes

### Scope Discipline (CRITICAL)
- Define specific scope before starting any work
- Only address identified issues - NO SCOPE CREEP
- Make minimal changes to address only identified issues
- Do not refactor unrelated code
- Do not add new features unless explicitly requested
- Focus on fixing what's broken, not improving what works

### Tool Compliance (MANDATORY)
- Use `make test` for test execution (NEVER direct pytest calls)
- Use `make test-cov` for test coverage
- Use `make lint` for code quality checks
- Use `make format` for code formatting
- Use `uv pip install` for package installation (NEVER direct pip calls)
- **NEVER use edit_tool on TOML files** (pyproject.toml, etc.) - use structured TOML libraries
- **NEVER use edit_tool on structured formats** - use appropriate structured libraries

### Git Workflow (MANDATORY)
- Create feature branch for all development work: `git checkout -b fix/[issue-description]`
- Use conventional commit format: `type(scope): description`
- Commit frequently with clear, descriptive messages
- Use `git diff main --name-only` to validate scope compliance
- Keep commits atomic and focused

### Rollback Strategy (IMMEDIATE EXECUTION)
If you detect ANY scope violation or unauthorized changes:
1. Stop development immediately
2. Document the violation
3. Execute: `git checkout main && git branch -D [feature-branch] && git clean -fd`
4. Restart PDCA cycle with corrected scope

## Test Scenario: Fix Failing Token Validation Test

### Current State
There is a failing test in `tests/test_authentication.py` that expects token validation with expiry checking. The test is currently failing because the authentication module doesn't exist.

### Your Task
Follow the PDCA methodology to fix this specific test failure. You must:

1. **PLAN**: Run tests, identify the specific failing test, define exact scope
2. **DO**: Read relevant files, understand what's needed
3. **CHECK**: Validate your understanding against test expectations
4. **ACT**: Implement minimal fix, add logging, validate

### Scope Definition (STRICT)
**ALLOWED**:
- Create `src/svg_image_generator/authentication.py` with minimal token validation
- Add logging for token expiry errors
- Update the specific failing test if needed

**FORBIDDEN**:
- Modify any other files
- Add new features beyond token validation
- Refactor unrelated code
- Improve code style of working code
- Add new dependencies

### Required Commands
- Use `make test` to run tests
- Use `make test-cov` for coverage
- Use `git checkout -b fix/token-validation-expiry` to create branch
- Use `git diff main --name-only` to validate scope

### Success Criteria
1. The specific failing test passes
2. Only the minimal required files are modified
3. All changes are within defined scope
4. Git workflow is followed correctly
5. No unauthorized modifications

## Instructions
1. Start by running `make test` to identify the failing test
2. Create a feature branch: `git checkout -b fix/token-validation-expiry`
3. Follow PDCA cycle strictly
4. Use only make commands for all operations
5. Validate scope compliance before each commit
6. If you detect any scope violation, execute rollback immediately

## Remember
- You are NOT here to improve the codebase
- You are NOT here to add new features
- You are ONLY here to fix the specific failing test
- Any deviation from scope = immediate rollback
- **NEVER use edit_tool on TOML files** - this is a critical rule violation
- Follow the rules exactly as written

Begin with the PLAN phase: run `make test` to identify the failing test.
