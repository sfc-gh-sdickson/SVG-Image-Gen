# Project Architecture for SVG Image Generation System

## 🏗️ System Overview

The SVG Image Generator is a Streamlit-based application that leverages Snowflake Cortex AI to generate SVG images from natural language descriptions. The system is designed for deployment in multiple environments with a focus on Streamlit in Snowflake (SiS) as the primary production target.

## 🎯 Architecture Principles

### 1. Multi-Environment Deployment
- **Primary Target**: Streamlit in Snowflake (SiS)
- **Secondary Target**: Package Distribution
- **Development**: Local environment with full tooling
- **Excluded**: Container deployment (user preference)

### 2. Layered Architecture
- **Presentation Layer**: Streamlit UI components
- **Business Logic Layer**: Session management, AI operations, storage
- **Data Access Layer**: Snowflake integration, file operations
- **Integration Layer**: Cortex AI, external services

### 3. Constraint Management
- **Environment Detection**: Runtime environment identification
- **Dependency Availability**: Package availability checking
- **Graceful Degradation**: Fallback mechanisms for missing features
- **Performance Optimization**: Environment-specific optimizations

## 🏛️ System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────┐
│           Presentation Layer        │
│         (Streamlit UI)              │
├─────────────────────────────────────┤
│           Business Logic Layer      │
│    (Session, AI, Storage Services)  │
├─────────────────────────────────────┤
│           Data Access Layer         │
│    (Snowflake DAO, File System)     │
├─────────────────────────────────────┤
│           Integration Layer         │
│    (Cortex AI, Streamlit)           │
└─────────────────────────────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    SVG Image Generator                      │
├─────────────────────────────────────────────────────────────┤
│  Session Manager  │  Context Discovery  │  AI Generation   │
│  - Auth Tiers     │  - Resources        │  - Cortex Calls  │
│  - Connection     │  - Permissions      │  - Prompt Refine │
│  - Fallback       │  - Validation       │  - Error Handle  │
├─────────────────────────────────────────────────────────────┤
│  Storage Service  │  Data Transport     │  Error Handling  │
│  - Stage Mgmt     │  - Nanoarrow        │  - Classification │
│  - File Ops       │  - Fallback         │  - Recovery      │
│  - Cleanup        │  - Performance      │  - Logging       │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Components

### 1. Session Management Service
```yaml
Purpose: Three-tier authentication and session management
Components:
  - Active Session Detection (Tier 1)
  - Connection Parameter Management (Tier 2)
  - Environment Variable Configuration (Tier 3)
  - Graceful Fallback Mechanisms
  - Connection Pooling
  - Error Recovery

Dependencies:
  - snowflake-snowpark-python[pandas]>=1.12.0
  - snowflake-connector-python>=3.0.0
  - cryptography>=41.0.0

Features:
  - Automatic environment detection
  - Seamless authentication switching
  - Connection health monitoring
  - Session caching and reuse
```

### 2. Context Discovery Service
```yaml
Purpose: Dynamic resource discovery and permission validation
Components:
  - Database Discovery
  - Schema Discovery
  - Stage Discovery
  - Cortex Model Discovery
  - Permission Validation
  - Resource Caching

Dependencies:
  - Snowflake session
  - SQL execution capabilities
  - Permission validation

Features:
  - Real-time resource discovery
  - Permission-based filtering
  - Cached resource lists
  - Error handling and recovery
```

### 3. AI Generation Service
```yaml
Purpose: Cortex AI integration and SVG generation
Components:
  - Model Validation
  - Prompt Engineering
  - Prompt Sandwich Implementation
  - Response Processing
  - Content Validation
  - Error Handling

Dependencies:
  - Snowflake session
  - Cortex AI service
  - Model registry

Features:
  - Multi-step prompt refinement
  - Model availability checking
  - Response validation
  - Timeout management
  - Retry logic
```

### 4. Storage Service
```yaml
Purpose: File storage and management in Snowflake stages
Components:
  - Stage Management
  - File Operations
  - Metadata Tracking
  - Resource Cleanup
  - Access Control

Dependencies:
  - Snowflake session
  - Stage permissions
  - File system operations

Features:
  - Automatic stage creation
  - File upload/download
  - Metadata management
  - Resource cleanup
  - Permission validation
```

### 5. Data Transport Service
```yaml
Purpose: Efficient data movement between Snowflake and Python
Components:
  - Nanoarrow Integration (Primary)
  - PyArrow Fallback (Legacy)
  - Performance Monitoring
  - Transport Layer Detection
  - Automatic Fallback

Dependencies:
  - snowflake-snowpark-python[pandas]>=1.12.0
  - nanoarrow (internal, managed by Snowflake)
  - pyarrow (fallback only)

Features:
  - Automatic transport layer selection
  - Performance benchmarking
  - Error rate monitoring
  - Automatic fallback mechanisms
  - Transport layer detection
```

## 🔐 Authentication Architecture

### Three-Tier Authentication System
```yaml
Tier 1 - Active Session (SiS Environment):
  - Method: get_active_session()
  - Environment: Streamlit in Snowflake
  - Security: Inherits user's Snowflake session
  - Fallback: Automatic to Tier 2

Tier 2 - Connection Parameters:
  - Method: Session.builder.create()
  - Environment: Various Snowflake environments
  - Security: Connection parameter validation
  - Fallback: Automatic to Tier 3

Tier 3 - Environment Variables:
  - Method: Session.builder.configs()
  - Environment: Local development
  - Security: Environment variable validation
  - Fallback: Error with guidance
```

### Authentication Flow
```
1. Try get_active_session() → Success: Use session
2. Try Session.builder.create() → Success: Use session
3. Try Session.builder.configs() → Success: Use session
4. All failed → Error with configuration guidance
```

## 📊 Data Architecture

### Data Transport Layer
```yaml
Primary Transport: Nanoarrow
  - Internal to Snowflake packages
  - Available in Snowpark >=1.12.0
  - Automatic selection
  - Optimized performance

Legacy Transport: PyArrow
  - Deprecated but available for fallback
  - Used only if nanoarrow fails
  - Performance monitoring required
  - Automatic rollback capability

Transport Detection:
  - Runtime capability detection
  - Performance benchmarking
  - Error rate monitoring
  - Automatic fallback triggers
```

### Data Flow
```
1. Snowflake Query → Snowpark DataFrame
2. DataFrame.to_pandas() → Nanoarrow Transport
3. Pandas DataFrame → Python Processing
4. Processed Data → Snowflake Storage
```

## 🚀 Deployment Architecture

### Streamlit in Snowflake (SiS) - Primary
```yaml
Environment: Snowflake-managed
Python Version: 3.9-3.11
Authentication: Tier 1 (active session)
Dependencies: Core only
Data Transport: Nanoarrow (internal)
Advantages:
  - Native Snowflake integration
  - Simplified authentication
  - Managed environment
  - Enterprise security
Constraints:
  - Limited package availability
  - Snowflake-managed environment
  - Python version constraints
```

### Package Distribution - Secondary
```yaml
Environment: User-managed
Python Version: >=3.9, <3.12
Authentication: All three tiers
Dependencies: Full control
Data Transport: Nanoarrow (internal)
Advantages:
  - Version control
  - Dependency management
  - Local development
  - Community distribution
Constraints:
  - User environment management
  - Installation complexity
  - Version compatibility
```

### Constraint Management Architecture
```yaml
Python Version Constraints:
  - Current: >=3.9, <3.12
  - Snowflake SiS: 3.9-3.11
  - Package Distribution: >=3.9, <3.12
  - Detection: Runtime version checking
  - Fallback: Graceful degradation

Package Availability Constraints:
  - Core Dependencies:
    - snowflake-snowpark-python[pandas]>=1.12.0
    - streamlit>=1.30
    - cryptography>=41.0.0
  - Optional Dependencies:
    - python-dotenv>=1.0.0
    - toml>=0.10.2
  - Detection: Import error handling
  - Fallback: Alternative implementations
```

### CI/CD Architecture
```yaml
Continuous Integration:
  - Code Quality:
    - Type checking (mypy)
    - Linting (ruff, flake8)
    - Security scanning (bandit)
    - Format validation (black)

  - Testing:
    - Unit tests (pytest)
    - Integration tests
    - Deployment tests
    - Type stub validation
    - Performance tests

  - Documentation:
    - README updates
    - API documentation
    - Ontology updates
    - Contributing guidelines

Continuous Deployment:
  - Automated Testing:
    - Pre-deployment validation
    - Smoke tests
    - Integration verification
    - Performance monitoring

  - Deployment Pipeline:
    - Environment preparation
    - Dependency installation
    - Configuration setup
    - Health checks
```

## 🎨 Performance Architecture

### Caching Architecture
```yaml
Session Caching:
  - Streamlit cache_resource decorator
  - Session object caching
  - Connection pooling
  - Health monitoring

Resource Caching:
  - Database list caching
  - Schema list caching
  - Stage list caching
  - Model list caching

Data Caching:
  - Query result caching
  - DataFrame caching
  - File content caching
  - Metadata caching
```

### Optimization Strategies
```yaml
Data Transport Optimization:
  - Nanoarrow for efficient serialization
  - Batch processing where possible
  - Minimal data transfer
  - Compression when beneficial

Query Optimization:
  - Efficient SQL queries
  - Proper indexing
  - Query result caching
  - Connection pooling

Memory Management:
  - Resource cleanup
  - Memory monitoring
  - Garbage collection
  - Memory-efficient operations
```

## 🔄 Error Handling Architecture

### Error Classification
```yaml
Authentication Errors:
  - Connection failures
  - Authentication failures
  - Permission errors
  - Configuration errors

Data Transport Errors:
  - Nanoarrow failures
  - PyArrow fallback errors
  - Serialization errors
  - Performance degradation

AI Service Errors:
  - Model unavailability
  - Service timeouts
  - Response validation errors
  - Content generation failures

Storage Errors:
  - Stage creation failures
  - File operation errors
  - Permission errors
  - Resource cleanup failures
```

### Error Recovery
```yaml
Automatic Recovery:
  - Retry logic
  - Fallback mechanisms
  - Circuit breakers
  - Graceful degradation

Manual Recovery:
  - Error reporting
  - User guidance
  - Rollback procedures
  - Support escalation

Monitoring:
  - Error rate tracking
  - Performance monitoring
  - Health checks
  - Alert systems
```

## 🔒 Security Architecture

### Authentication Security
```yaml
Session Security:
  - Inherits Snowflake security
  - Role-based access control
  - Session timeout management
  - Secure credential handling

Data Security:
  - Encrypted connections
  - Secure file operations
  - Input validation
  - Output sanitization

Access Control:
  - Permission validation
  - Resource-level access
  - Audit logging
  - Compliance monitoring
```

### Data Protection
```yaml
Data in Transit:
  - Encrypted connections
  - Secure protocols
  - Certificate validation
  - Connection security

Data at Rest:
  - Snowflake security
  - File encryption
  - Access controls
  - Audit trails

Data Processing:
  - Input validation
  - Output sanitization
  - Memory protection
  - Resource isolation
```

## 📈 Scalability Architecture

### Horizontal Scaling
```yaml
Stateless Design:
  - No server-side state
  - Session-based state management
  - Stateless operations
  - Load balancing support

Resource Management:
  - Connection pooling
  - Resource cleanup
  - Memory management
  - Performance optimization

Load Distribution:
  - Multiple instances
  - Load balancing
  - Resource sharing
  - Performance monitoring
```

### Vertical Scaling
```yaml
Resource Optimization:
  - Memory optimization
  - CPU optimization
  - I/O optimization
  - Network optimization

Performance Tuning:
  - Query optimization
  - Caching strategies
  - Connection pooling
  - Resource management
```

## 🧪 Testing Architecture

### Test Categories
```yaml
Unit Tests:
  - Component testing
  - Function testing
  - Mock testing
  - Isolation testing

Integration Tests:
  - Component integration
  - Service integration
  - End-to-end testing
  - Performance testing

Deployment Tests:
  - Environment testing
  - Configuration testing
  - Dependency testing
  - Compatibility testing
```

### Test Environment
```yaml
Local Development:
  - Full test suite
  - Mock services
  - Local databases
  - Development tools

CI/CD Pipeline:
  - Automated testing
  - Integration testing
  - Performance testing
  - Security testing

Production Testing:
  - Smoke tests
  - Health checks
  - Performance monitoring
  - Error tracking
```

## 📚 Documentation Architecture

### Technical Documentation
```yaml
Architecture Documentation:
  - System overview
  - Component documentation
  - Integration guides
  - Deployment guides

API Documentation:
  - Function documentation
  - Parameter documentation
  - Return value documentation
  - Example usage

Configuration Documentation:
  - Environment setup
  - Configuration options
  - Dependency management
  - Troubleshooting guides
```

### User Documentation
```yaml
Installation Guides:
  - Environment setup
  - Dependency installation
  - Configuration setup
  - Verification steps

Usage Guides:
  - Feature documentation
  - Workflow guides
  - Best practices
  - Troubleshooting

Maintenance Guides:
  - Update procedures
  - Backup procedures
  - Monitoring guides
  - Support procedures
```

## 🔄 Migration Architecture

### PyArrow to NanoArrow Migration
```yaml
Status: COMPLETED
Version: 1.1.0
Migration Date: 2025-01-27

Migration Strategy:
  - Gradual migration
  - Feature flags
  - Fallback mechanisms
  - Performance monitoring

Validation:
  - SiS environment testing
  - Performance benchmarking
  - Error rate monitoring
  - Rollback testing

Rollback Plan:
  - Automatic fallback
  - Performance alerts
  - Error rate thresholds
  - Manual intervention
```

### Future Migrations
```yaml
Planning:
  - Impact assessment
  - Risk analysis
  - Rollback planning
  - Testing strategy

Execution:
  - Gradual rollout
  - Monitoring
  - Validation
  - Documentation

Maintenance:
  - Performance monitoring
  - Error tracking
  - User feedback
  - Continuous improvement
```
