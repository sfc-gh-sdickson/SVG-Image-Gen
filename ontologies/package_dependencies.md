# Package Dependencies for SVG Image Generation System

## Core Package Dependencies

### 1. Streamlit Framework
```yaml
Package: streamlit
Version: >=1.30
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
Constraints:
  - Required for all deployment scenarios
  - Version compatibility with Snowflake SiS
  - UI component API compliance
```

### 2. Snowflake Snowpark for Python
```yaml
Package: snowflake-snowpark-python
Version: >=1.12.0
Purpose: Native Python library for Snowflake data programming
Usage:
  - Three-tier authentication system:
    1. Active session management (get_active_session)
    2. Connection parameter detection (Session.builder.create)
    3. Environment variable configuration (Session.builder.configs)
  - SQL query execution
  - DataFrame operations (using nanoarrow internally)
  - File operations with stages
  - Transaction management
Dependencies:
  - snowflake-connector-python
  - nanoarrow (internal, managed by Snowpark)
  - numpy
  - pandas
Constraints:
  - Critical dependency for all Snowflake operations
  - Version compatibility with Snowflake platform
  - Python version constraints (3.9-3.11 for SiS)
  - Nanoarrow integration available in >=1.12.0
```

### 3. Snowflake Connector for Python
```yaml
Package: snowflake-connector-python
Version: >=3.0.0
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
  - nanoarrow (internal, managed by connector)
Constraints:
  - Required for Snowpark functionality
  - Security updates and vulnerability patches
  - Compatibility with authentication methods
```

### 4. Nanoarrow (Internal)
```yaml
Package: nanoarrow
Version: Internal (managed by Snowflake packages)
Purpose: Lightweight Arrow-compatible serialization layer
Usage:
  - Internal data format handling
  - Performance optimization
  - Snowflake data exchange
  - DataFrame transport
Dependencies:
  - Managed internally by Snowflake packages
Constraints:
  - Internal dependency, not directly managed
  - Available in Snowpark >=1.12.0
  - Used automatically by Snowflake packages
  - No explicit installation required
```

### 5. Cryptography
```yaml
Package: cryptography
Version: >=41.0.0
Purpose: Cryptographic operations and security
Usage:
  - Private key authentication
  - Secure credential handling
  - Encryption/decryption operations
Dependencies:
  - cffi
  - six
Constraints:
  - Security requirement for authentication
  - Version updates for vulnerability patches
  - Required for private key handling
```

### 6. Python-dotenv
```yaml
Package: python-dotenv
Version: >=1.0.0
Purpose: Environment variable management for local development
Usage:
  - Load environment variables from .env files
  - Support for local development without global env pollution
  - Seamless transition between local and production environments
Dependencies:
  - None (pure Python)
Constraints:
  - Optional for SiS deployment
  - Required for local development
  - Not needed in package distribution
```

### 7. TOML
```yaml
Package: toml
Version: >=0.10.2
Purpose: TOML configuration file parsing
Usage:
  - connections.toml file parsing
  - Configuration management
  - Settings file handling
Dependencies:
  - None (pure Python)
Constraints:
  - Required for connections.toml support
  - Used in Tier 2 authentication
  - Optional for SiS deployment
```

## Deprecated Dependencies

### PyArrow (Deprecated)
```yaml
Package: pyarrow
Version: <19.0.0 (deprecated)
Purpose: Previously used for data serialization and processing
Usage:
  - Was used for data format handling
  - Was used for performance optimization
  - Was used for Snowflake data exchange
Status: DEPRECATED
Replacement: nanoarrow (internal, managed by Snowflake packages)
Migration: Completed in version 1.1.0
Constraints:
  - No longer required for runtime
  - May be kept in dev dependencies for legacy testing
  - Rollback available if needed
```

## Deployment-Specific Dependencies

### 1. Streamlit in Snowflake (SiS) Dependencies
```yaml
Required Core Dependencies:
  - streamlit>=1.30
  - snowflake-snowpark-python[pandas]>=1.12.0
  - snowflake-connector-python>=3.0.0
  - cryptography>=41.0.0

Optional Dependencies:
  - toml>=0.10.2 (for connections.toml support)
  - python-dotenv>=1.0.0 (not typically needed)

Not Required:
  - pyarrow (deprecated, replaced by nanoarrow)
  - Development dependencies
  - Type stubs (handled by Snowflake environment)
  - Testing frameworks
  - Code quality tools

Constraints:
  - Python version: 3.9-3.11
  - Package availability: Limited to Snowflake-approved packages
  - Environment: Snowflake-managed
  - Authentication: Primarily Tier 1 (active session)
  - Data transport: nanoarrow (internal)
```

### 2. Package Distribution Dependencies
```yaml
Required Core Dependencies:
  - streamlit>=1.30
  - snowflake-snowpark-python[pandas]>=1.12.0
  - snowflake-connector-python>=3.0.0
  - cryptography>=41.0.0
  - python-dotenv>=1.0.0
  - toml>=0.10.2

Optional Dependencies:
  - All development dependencies
  - Type stubs for comprehensive checking
  - Testing frameworks
  - Code quality tools

Constraints:
  - Python version: >=3.9, <3.12
  - Package availability: Full PyPI access
  - Environment: User-managed
  - Authentication: All three tiers supported
  - Data transport: nanoarrow (internal)
```

## Development Dependencies

### 1. Type Checking and Stub Management
```yaml
Package: mypy
Version: >=1.0.0
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
Version: >=23.0.0
Purpose: Code formatter
Usage:
  - Consistent code formatting
  - PEP 8 compliance
  - Pre-commit formatting

Package: ruff
Version: >=0.1.0
Purpose: Fast Python linter
Usage:
  - Code linting
  - Import sorting
  - Style enforcement

Package: flake8
Version: >=6.0.0
Purpose: Style guide enforcement
Usage:
  - PEP 8 compliance checking
  - Code complexity analysis
  - Style consistency

Package: isort
Version: >=5.12.0
Purpose: Import sorting
Usage:
  - Consistent import organization
  - Pre-commit import sorting
```

### 3. Testing Framework
```yaml
Package: pytest
Version: >=7.0.0
Purpose: Testing framework
Usage:
  - Unit testing
  - Integration testing
  - Test discovery and execution
  - Coverage reporting

Package: pytest-mock
Version: >=3.10.0
Purpose: Mocking utilities for pytest
Usage:
  - Mock objects for testing
  - Dependency injection testing
  - Isolated unit tests

Package: pytest-cov
Version: >=4.0.0
Purpose: Coverage reporting for pytest
Usage:
  - Code coverage measurement
  - Coverage reporting
  - Coverage thresholds
```

### 4. Security and Quality Assurance
```yaml
Package: bandit
Version: >=1.7.0
Purpose: Security linter
Usage:
  - Security vulnerability detection
  - Common security issue identification
  - Pre-commit security checks

Package: safety
Version: >=2.0.0
Purpose: Dependency vulnerability scanner
Usage:
  - Known vulnerability detection
  - Dependency security monitoring
  - CI/CD security integration
```

## Constraint Management System

### 1. Python Version Constraints
```yaml
Current Requirements:
  - requires-python: ">=3.9, <3.12"

Environment-Specific Constraints:
  - Snowflake SiS: 3.9-3.11
  - Local Development: >=3.9, <3.12
  - Package Distribution: >=3.9, <3.12

Detection Mechanisms:
  - Runtime version checking
  - Environment detection
  - Graceful degradation
  - User notification

Fallback Strategies:
  - Version-specific code paths
  - Alternative implementations
  - Feature disabling
  - Error messaging
```

### 2. Package Availability Constraints
```yaml
Core Dependencies (Always Required):
  - snowflake-snowpark-python[pandas]>=1.12.0
  - streamlit>=1.30
  - cryptography>=41.0.0

Optional Dependencies (Environment-Dependent):
  - python-dotenv>=1.0.0 (local development)
  - toml>=0.10.2 (connections.toml support)

Deprecated Dependencies:
  - pyarrow<19.0.0 (deprecated, replaced by nanoarrow)

Detection Mechanisms:
  - Import error handling
  - Runtime dependency checking
  - Graceful degradation
  - Fallback to legacy methods

Fallback Strategies:
  - Alternative implementations
  - Feature disabling
  - Error messaging
  - Rollback procedures
```

### 3. Data Transport Constraints
```yaml
Primary Transport Layer:
  - nanoarrow (internal, managed by Snowflake packages)
  - Available in Snowpark >=1.12.0
  - Automatic selection by Snowflake packages

Legacy Transport Layer:
  - pyarrow (deprecated, fallback only)
  - Available for rollback scenarios
  - Performance monitoring required

Detection Mechanisms:
  - Runtime transport layer detection
  - Performance benchmarking
  - Error rate monitoring
  - Automatic fallback

Fallback Strategies:
  - Automatic rollback to pyarrow
  - Performance degradation alerts
  - Error rate threshold monitoring
  - Manual intervention triggers
```

## Migration Status

### PyArrow to NanoArrow Migration
```yaml
Status: COMPLETED
Version: 1.1.0
Migration Date: 2025-01-27

Changes Made:
  - Removed pyarrow from runtime dependencies
  - Updated to snowflake-snowpark-python[pandas]>=1.12.0
  - Implemented nanoarrow-based data transport
  - Added rollback mechanisms
  - Updated documentation

Validation:
  - SiS environment testing completed
  - Performance benchmarks established
  - Rollback procedures tested
  - Error handling validated

Rollback Plan:
  - Automatic fallback to pyarrow if needed
  - Performance monitoring in place
  - Error rate threshold alerts
  - Manual rollback procedures documented
```

This comprehensive dependency management system ensures reliable, secure, and maintainable development with automated quality assurance and flexible deployment options. The constraint management system handles Python version and package availability limitations across different deployment environments.
