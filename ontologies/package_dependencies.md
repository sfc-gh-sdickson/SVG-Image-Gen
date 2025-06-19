# Package Dependencies for SVG Image Generation System

## Core Package Dependencies

### 1. Streamlit Framework
```yaml
Package: streamlit
Version: >= 1.28.0
Purpose: Web application framework for creating interactive data apps
Usage:
  - Main UI framework
  - Session state management
  - Component rendering
  - File upload/download interface
  - Real-time updates
Dependencies:
  - click
  - protobuf
  - packaging
  - toml
  - watchdog
```

### 2. Snowflake Snowpark for Python
```yaml
Package: snowflake-snowpark-python
Version: >= 1.8.0
Purpose: Native Python library for Snowflake data programming
Usage:
  - Snowflake session management
  - SQL query execution
  - DataFrame operations
  - File operations with stages
  - Transaction management
Dependencies:
  - snowflake-connector-python
  - pyarrow
  - numpy
  - pandas
```

### 3. Snowflake Connector for Python
```yaml
Package: snowflake-connector-python
Version: >= 3.0.0
Purpose: Python connector for Snowflake database
Usage:
  - Database connection management
  - Authentication handling
  - Query execution
  - Result set processing
Dependencies:
  - cryptography
  - requests
  - urllib3
  - certifi
```

### 4. Python-dotenv
```yaml
Package: python-dotenv
Version: >= 1.0.0
Purpose: Environment variable management for local development
Usage:
  - Load environment variables from .env files
  - Support for local development without global env pollution
  - Seamless transition between local and production environments
Dependencies:
  - None (pure Python)
```

## Development Dependencies

### 1. Type Checking and Stub Management
```yaml
Package: mypy
Version: >= 1.0.0
Purpose: Static type checking for Python
Usage:
  - Type validation
  - Code quality assurance
  - IDE integration support
  - Pre-commit validation

Package: types-*
Version: Various
Purpose: Type stubs for third-party packages
Usage:
  - Provide type information for external libraries
  - Enable comprehensive type checking
  - Improve IDE autocomplete and error detection
Management:
  - Automatic detection via scripts/fix-missing-type-stubs.py
  - Pre-commit integration for automatic stub management
  - Comprehensive package mapping for common libraries
```

### 2. Code Quality Tools
```yaml
Package: black
Version: >= 23.0.0
Purpose: Code formatter
Usage:
  - Consistent code formatting
  - PEP 8 compliance
  - Pre-commit formatting

Package: ruff
Version: >= 0.1.0
Purpose: Fast Python linter
Usage:
  - Code linting
  - Import sorting
  - Style enforcement

Package: flake8
Version: >= 6.0.0
Purpose: Style guide enforcement
Usage:
  - PEP 8 compliance checking
  - Code complexity analysis
  - Style consistency

Package: isort
Version: >= 5.12.0
Purpose: Import sorting
Usage:
  - Consistent import organization
  - Pre-commit import sorting
```

### 3. Testing Framework
```yaml
Package: pytest
Version: >= 7.0.0
Purpose: Testing framework
Usage:
  - Unit testing
  - Integration testing
  - Test discovery and execution
  - Coverage reporting

Package: pytest-mock
Version: >= 3.10.0
Purpose: Mocking utilities for pytest
Usage:
  - Mock objects for testing
  - Dependency injection testing
  - Isolated unit tests

Package: pytest-cov
Version: >= 4.0.0
Purpose: Coverage reporting for pytest
Usage:
  - Code coverage measurement
  - Coverage reporting
  - Coverage thresholds
```

### 4. Security and Quality Assurance
```yaml
Package: bandit
Version: >= 1.7.0
Purpose: Security linter
Usage:
  - Security vulnerability detection
  - Common security issue identification
  - Pre-commit security checks

Package: safety
Version: >= 2.0.0
Purpose: Dependency vulnerability scanner
Usage:
  - Known vulnerability detection
  - Dependency security monitoring
  - CI/CD security integration
```

## Type Stub Management Workflow

### 1. Automatic Stub Detection
```yaml
Script: scripts/fix-missing-type-stubs.py
Purpose: Automatic type stub management
Features:
  - Parses mypy output for missing stubs
  - Maps package names to typeshed equivalents
  - Updates requirements-dev.txt automatically
  - Optional automatic installation
  - Comprehensive package mapping (80+ packages)
  - Built-in module handling
```

### 2. Pre-commit Integration
```yaml
Hook: fix-missing-type-stubs
Trigger: Before each commit
Actions:
  - Run mypy on codebase
  - Detect missing type stubs
  - Add missing stubs to requirements-dev.txt
  - Install new stubs if needed
  - Ensure clean commits
```

### 3. Package Mapping Strategy
```yaml
Mapping Categories:
  - Standard library mappings (yaml -> PyYAML)
  - Common third-party packages (requests, flask, etc.)
  - Database and ORM packages
  - Web frameworks and tools
  - Cloud and deployment packages
  - Data processing and analysis
  - Testing and mocking tools
  - Development tools

Built-in Handling:
  - Skip built-in modules (xml, json, csv, etc.)
  - Map pkg_resources to setuptools
  - Handle special cases (yaml -> PyYAML)
```

## Dependency Management Tools

### 1. UV (Recommended)
```yaml
Tool: uv
Purpose: Fast Python package installer and resolver
Advantages:
  - Significantly faster than pip
  - Better dependency resolution
  - Built-in virtual environment management
  - Lock file support
  - Modern Python packaging standards
Usage:
  - uv pip install -r requirements.txt
  - uv pip install -r requirements-dev.txt
  - uv run python script.py
```

### 2. Pip (Traditional)
```yaml
Tool: pip
Purpose: Traditional Python package installer
Usage:
  - pip install -r requirements.txt
  - pip install -r requirements-dev.txt
  - Compatible with all Python environments
```

## Environment-Specific Dependencies

### 1. Local Development
```yaml
Required:
  - python-dotenv (environment variable loading)
  - All development dependencies
  - Type stubs for used packages

Optional:
  - uv (for faster dependency management)
  - Additional type stubs as needed
```

### 2. Streamlit in Snowflake (SiS)
```yaml
Required:
  - Core runtime dependencies only
  - No local environment setup needed
  - Automatic session management

Not Required:
  - python-dotenv
  - Development dependencies
  - Type stubs (handled by Snowflake environment)
```

### 3. CI/CD Environment
```yaml
Required:
  - All development dependencies
  - Type stubs for comprehensive checking
  - Security scanning tools
  - Coverage reporting tools

Optional:
  - Documentation generation tools
  - Performance testing tools
```

## Dependency Update Workflow

### 1. Regular Updates
```yaml
Process:
  - Monthly dependency review
  - Security vulnerability scanning
  - Type stub compatibility checking
  - Automated testing after updates
  - Documentation updates
```

### 2. Type Stub Updates
```yaml
Process:
  - Automatic detection via helper script
  - Manual review of new stubs
  - Testing with updated stubs
  - Documentation updates
  - Team communication about changes
```

## Security Considerations

### 1. Dependency Scanning
```yaml
Tools:
  - safety (vulnerability scanning)
  - bandit (code security analysis)
  - pre-commit hooks (automated checks)

Frequency:
  - Pre-commit (automatic)
  - CI/CD pipeline (automatic)
  - Monthly manual review
```

### 2. Type Stub Security
```yaml
Considerations:
  - Only install stubs from trusted sources (typeshed)
  - Regular updates for security patches
  - Validation of stub compatibility
  - Testing with new stub versions
```

## Performance Optimization

### 1. Installation Optimization
```yaml
Strategies:
  - Use uv for faster installations
  - Lock files for reproducible builds
  - Minimal dependency sets
  - Regular cleanup of unused dependencies
```

### 2. Runtime Optimization
```yaml
Strategies:
  - Lazy loading where appropriate
  - Minimal import statements
  - Efficient type checking configuration
  - Caching for repeated operations
```

## Monitoring and Maintenance

### 1. Dependency Health
```yaml
Metrics:
  - Update frequency
  - Security vulnerability count
  - Type stub coverage
  - Build time impact
  - Runtime performance impact
```

### 2. Maintenance Tasks
```yaml
Regular Tasks:
  - Update dependencies
  - Review and update type stubs
  - Clean up unused dependencies
  - Update documentation
  - Test compatibility
```

This comprehensive dependency management system ensures reliable, secure, and maintainable code with excellent developer experience through automated type stub management.
