# SVG Image Generation Project Architecture

## System Overview

The SVG Image Generation project is a Streamlit-based web application that leverages Snowflake Cortex AI to generate SVG images from natural language descriptions. The system integrates with Snowflake's data platform for storage, compute, and AI capabilities.

## Core Components

### 1. Frontend Layer (Streamlit UI)
- **Technology**: Streamlit framework
- **Purpose**: User interface for SVG generation and configuration
- **Key Features**:
  - Text input for SVG descriptions
  - Model selection dropdown
  - File naming interface
  - Real-time SVG preview
  - Stage management interface

### 2. Backend Layer (Snowflake Integration)
- **Technology**: Snowpark for Python
- **Purpose**: Data processing and Snowflake operations
- **Key Features**:
  - Session management
  - SQL query execution
  - File operations
  - Stage management

### 3. AI Layer (Snowflake Cortex)
- **Technology**: Snowflake Cortex AI
- **Purpose**: SVG generation from text prompts
- **Supported Models**:
  - `openai-gpt-4.1`
  - `claude-4-sonnet`
  - `claude-3-7-sonnet`
  - `claude-3-5-sonnet`

### 4. Storage Layer (Snowflake Stages)
- **Technology**: Snowflake internal stages
- **Purpose**: SVG file storage and retrieval
- **Features**:
  - Automatic stage creation
  - File upload/download
  - Metadata tracking

## Data Flow Architecture

```
User Input → Streamlit UI → Snowpark Session → Cortex AI → SVG Generation → Stage Storage → File Retrieval
```

### Detailed Flow:
1. **User Input**: Text description + configuration
2. **Session Management**: Active Snowflake session validation
3. **Context Switching**: Database/schema switching if needed
4. **AI Processing**: Cortex prompt generation and execution
5. **Content Processing**: SVG extraction and validation
6. **Storage**: Temporary table → Stage upload
7. **Cleanup**: Temporary resource removal
8. **Output**: File location and retrieval instructions

## Functional Dependencies

### Core Dependencies
- **streamlit**: Web application framework
- **snowflake-snowpark-python**: Snowflake data programming
- **datetime**: Timestamp generation
- **tempfile**: Temporary file handling
- **os**: Operating system operations

### External Dependencies
- **Snowflake Account**: With Cortex AI enabled
- **Streamlit in Snowflake (SiS)**: Runtime environment
- **Network Connectivity**: For Snowflake API calls

## Security Model

### Authentication
- Uses active Snowflake session
- No additional authentication required
- Inherits user's Snowflake permissions

### Authorization
- Requires CREATE STAGE privileges
- Needs warehouse access
- Requires Cortex AI access
- Schema-level permissions for table operations

### Data Protection
- Temporary tables are transient
- Automatic cleanup of temporary resources
- No persistent storage of sensitive data

## Performance Considerations

### Optimization Strategies
- Cached session management
- Transient table usage
- Efficient file format handling
- Minimal data transfer

### Scalability
- Stateless application design
- Resource cleanup after each operation
- Configurable warehouse sizing
- Parallel processing capabilities

## Error Handling

### Exception Categories
1. **Session Errors**: Connection failures
2. **Permission Errors**: Insufficient privileges
3. **AI Generation Errors**: Cortex API failures
4. **Storage Errors**: Stage operation failures
5. **Validation Errors**: Invalid input data

### Recovery Mechanisms
- Graceful degradation
- User-friendly error messages
- Automatic resource cleanup
- Retry logic for transient failures

## Monitoring and Observability

### Key Metrics
- Generation success rate
- Processing time
- File upload success rate
- Error frequency by type

### Logging
- Session establishment
- AI generation requests
- File operations
- Error conditions

## Deployment Architecture

### Environment Requirements
- Snowflake account with SiS enabled
- Cortex AI access
- Appropriate role permissions
- Network access to Snowflake APIs

### Configuration Management
- Stage naming conventions
- Model selection options
- File naming patterns
- Context switching rules 