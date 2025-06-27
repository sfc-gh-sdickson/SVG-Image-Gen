# Functional Dependencies for SVG Image Generation System

## 🔗 Core Functional Dependencies

### 1. Authentication and Session Management

#### A. Session Creation Dependencies
```yaml
Function: get_session()
Dependencies:
  - snowflake-snowpark-python[pandas]>=1.12.0 package
  - Three-tier authentication system:
    1. Active Snowflake connection (SiS environment) - get_active_session()
    2. Connection parameters (various Snowflake environments) - Session.builder.create()
    3. Environment variables (local development) - Session.builder.configs()
  - python-dotenv package (local development)
  - Valid user credentials
  - Network connectivity to Snowflake
  - Streamlit cache_resource decorator
Output: Snowflake session object
Error Handling: Connection failure, authentication errors, missing environment variables
Authentication Flow:
  1. Try get_active_session() for SiS environment
  2. Try Session.builder.create() for connection parameter environments
  3. Try Session.builder.configs() with environment variables for local development
```

#### B. Context Management Dependencies
```yaml
Function: use_context()
Dependencies:
  - Valid Snowflake session
  - Database existence (if specified)
  - Schema existence (if specified)
  - User permissions for database/schema
  - SQL execution capabilities
Output: Boolean success status
Error Handling: Invalid context, permission errors
```

#### C. Model Discovery and Validation Dependencies
```yaml
Function: get_available_cortex_models(), validate_cortex_model()
Dependencies:
  - Valid Snowflake session
  - Cortex AI service enabled
  - User permissions for Cortex models
  - Model registry or test queries
Output: List of available models, Boolean validation result
Error Handling: Unknown model, permission errors, service errors, timeouts
```

#### D. SVG Generation Dependencies
```yaml
Function: generate_svg_content(), implement_prompt_sandwich(), safe_cortex_call()
Dependencies:
  - Valid prompt text
  - Selected AI model availability (validated)
  - Cortex AI service access
  - Snowflake warehouse running
  - SQL execution permissions
  - Network connectivity
Output: SVG content string
Error Handling: Model failures, timeouts, content validation errors, service errors
```

### 2. Data Transport Dependencies

#### A. DataFrame Operations Dependencies
```yaml
Function: session.sql().to_pandas(), session.table().to_pandas()
Dependencies:
  - snowflake-snowpark-python[pandas]>=1.12.0
  - nanoarrow (internal, managed by Snowflake packages)
  - Valid Snowflake session
  - SQL execution permissions
  - Network connectivity
  - Memory for DataFrame storage
Output: Pandas DataFrame
Error Handling: Transport failures, memory errors, permission errors
Transport Layer:
  - Primary: nanoarrow (internal, automatic)
  - Fallback: pyarrow (if available and needed)
  - Detection: Runtime capability detection
```

#### B. Data Serialization Dependencies
```yaml
Function: DataFrame serialization/deserialization
Dependencies:
  - nanoarrow (internal, managed by Snowflake)
  - Memory allocation for data
  - Network bandwidth for data transfer
  - CPU for serialization processing
Output: Serialized/deserialized data
Error Handling: Serialization errors, memory errors, network errors
Performance Monitoring:
  - Serialization time
  - Memory usage
  - Network transfer time
  - Error rates
```

### 3. Storage and File Management Dependencies

#### A. Stage Management Dependencies
```yaml
Function: create_stage(), list_stages(), drop_stage()
Dependencies:
  - Valid Snowflake session
  - CREATE STAGE permissions
  - Database and schema access
  - Storage quota availability
Output: Stage creation/management status
Error Handling: Permission errors, quota exceeded, storage errors
```

#### B. File Operations Dependencies
```yaml
Function: upload_file(), download_file(), delete_file()
Dependencies:
  - Valid Snowflake session
  - Stage access permissions
  - File system access (local)
  - Network connectivity
  - Storage space availability
Output: File operation status
Error Handling: Permission errors, network errors, storage errors
```

#### C. Metadata Management Dependencies
```yaml
Function: store_metadata(), retrieve_metadata(), update_metadata()
Dependencies:
  - Valid Snowflake session
  - Table creation permissions
  - Data insertion permissions
  - Query execution permissions
Output: Metadata operation status
Error Handling: Permission errors, data errors, constraint violations
```

### 4. AI Service Dependencies

#### A. Cortex AI Integration Dependencies
```yaml
Function: SNOWFLAKE.CORTEX.COMPLETE()
Dependencies:
  - Valid Snowflake session
  - Cortex AI service enabled
  - User permissions for Cortex
  - Model availability
  - Network connectivity to AI service
  - Warehouse running
Output: AI-generated content
Error Handling: Service errors, model errors, timeout errors, permission errors
```

#### B. Prompt Engineering Dependencies
```yaml
Function: refine_prompt(), implement_prompt_sandwich()
Dependencies:
  - Valid prompt input
  - AI model capabilities
  - Context information
  - User preferences
  - Content validation rules
Output: Refined prompt
Error Handling: Invalid input, model limitations, validation errors
```

### 5. Error Handling and Recovery Dependencies

#### A. Error Classification Dependencies
```yaml
Function: classify_error(), handle_error()
Dependencies:
  - Error information
  - Error classification rules
  - Context information
  - Recovery strategies
Output: Error classification and handling plan
Error Handling: Classification failures, recovery failures
```

#### B. Recovery Mechanism Dependencies
```yaml
Function: retry_operation(), fallback_operation()
Dependencies:
  - Original operation
  - Retry configuration
  - Fallback options
  - Success criteria
  - Timeout settings
Output: Operation result or fallback result
Error Handling: Retry exhaustion, fallback failures
```

## 🔄 Data Flow Dependencies

### 1. Primary Data Flow
```yaml
Flow: User Input → Session → Context → AI → Storage → Output
Dependencies:
  - User input validation
  - Session establishment
  - Context discovery
  - AI service availability
  - Storage access
  - Output formatting
Error Handling: Flow interruption, partial failures, rollback
```

### 2. Error Recovery Flow
```yaml
Flow: Error Detection → Classification → Recovery → Continuation
Dependencies:
  - Error detection mechanisms
  - Classification rules
  - Recovery strategies
  - State management
  - User notification
Error Handling: Recovery failures, cascading errors
```

## 🛠️ Technical Dependencies

### 1. Runtime Dependencies
```yaml
Core Runtime:
  - streamlit>=1.30
  - snowflake-snowpark-python[pandas]>=1.12.0
  - snowflake-connector-python>=3.0.0
  - cryptography>=41.0.0

Optional Runtime:
  - python-dotenv>=1.0.0 (local development)
  - toml>=0.10.2 (connections.toml support)

Internal Dependencies:
  - nanoarrow (managed by Snowflake packages)
  - numpy (managed by Snowpark)
  - pandas (managed by Snowpark)
```

### 2. Development Dependencies
```yaml
Testing:
  - pytest>=7.0.0
  - pytest-mock>=3.10.0
  - pytest-cov>=4.0.0

Code Quality:
  - black>=23.0.0
  - flake8>=6.0.0
  - mypy>=1.0.0

Security:
  - bandit>=1.7.0
  - safety>=2.0.0
```

### 3. Environment Dependencies
```yaml
SiS Environment:
  - Python 3.9-3.11
  - Snowflake-managed environment
  - Limited package availability
  - Active session authentication

Local Development:
  - Python >=3.9, <3.12
  - Full package availability
  - All authentication methods
  - Development tools

Package Distribution:
  - Python >=3.9, <3.12
  - Full package availability
  - All authentication methods
  - User-managed environment
```

## 🔐 Security Dependencies

### 1. Authentication Dependencies
```yaml
Tier 1 - Active Session:
  - Snowflake session management
  - Session validation
  - Permission inheritance
  - Session timeout handling

Tier 2 - Connection Parameters:
  - connections.toml file
  - Parameter validation
  - Private key handling
  - Certificate validation

Tier 3 - Environment Variables:
  - Environment variable access
  - Credential validation
  - Secure storage
  - Access control
```

### 2. Authorization Dependencies
```yaml
Role-Based Access:
  - User role validation
  - Permission checking
  - Resource access control
  - Audit logging

Resource Permissions:
  - Database access
  - Schema access
  - Stage access
  - Table access
  - AI service access
```

## 📊 Performance Dependencies

### 1. Data Transport Performance
```yaml
Nanoarrow Transport:
  - Efficient serialization
  - Minimal memory usage
  - Fast data transfer
  - Optimized for Snowflake

Performance Monitoring:
  - Transport time measurement
  - Memory usage tracking
  - Error rate monitoring
  - Performance alerts
```

### 2. Caching Dependencies
```yaml
Session Caching:
  - Streamlit cache_resource
  - Session object caching
  - Connection pooling
  - Cache invalidation

Data Caching:
  - Query result caching
  - Resource list caching
  - Metadata caching
  - Cache management
```

## 🔄 Migration Dependencies

### 1. PyArrow to NanoArrow Migration
```yaml
Migration Status: COMPLETED
Version: 1.1.0
Migration Date: 2025-01-27

Dependencies:
  - snowflake-snowpark-python[pandas]>=1.12.0
  - nanoarrow (internal, managed by Snowflake)
  - pyarrow (fallback only)

Validation:
  - SiS environment testing
  - Performance benchmarking
  - Error rate monitoring
  - Rollback testing

Rollback Plan:
  - Automatic fallback to pyarrow
  - Performance monitoring
  - Error rate alerts
  - Manual intervention
```

### 2. Version Alignment Dependencies
```yaml
Version Requirements:
  - All configuration files aligned
  - Consistent version constraints
  - Dependency compatibility
  - Environment compatibility

Validation:
  - Version consistency checking
  - Dependency resolution
  - Compatibility testing
  - Deployment validation
```

## 🧪 Testing Dependencies

### 1. Test Environment Dependencies
```yaml
Unit Testing:
  - pytest framework
  - Mock objects
  - Test data
  - Isolation mechanisms

Integration Testing:
  - Snowflake test environment
  - AI service access
  - Network connectivity
  - Test data management

End-to-End Testing:
  - Complete environment
  - Real data flows
  - Performance testing
  - Error scenario testing
```

### 2. Test Data Dependencies
```yaml
Test Data Management:
  - Test database setup
  - Test schema creation
  - Test data generation
  - Data cleanup

Mock Services:
  - Snowflake session mocking
  - AI service mocking
  - File system mocking
  - Network mocking
```

## 📈 Monitoring Dependencies

### 1. Performance Monitoring
```yaml
Metrics Collection:
  - Response time measurement
  - Memory usage tracking
  - Error rate monitoring
  - Resource utilization

Alerting:
  - Performance thresholds
  - Error rate thresholds
  - Resource usage alerts
  - Service availability alerts
```

### 2. Logging Dependencies
```yaml
Structured Logging:
  - Log format specification
  - Log level configuration
  - Log storage management
  - Log analysis tools

Audit Logging:
  - User action logging
  - System event logging
  - Security event logging
  - Compliance reporting
```

This comprehensive dependency mapping ensures that all functional requirements are properly identified and managed throughout the system lifecycle.
