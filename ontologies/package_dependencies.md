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

## Standard Library Dependencies

### 1. DateTime Module
```yaml
Module: datetime
Purpose: Date and time manipulation
Usage:
  - Timestamp generation for filenames
  - Session tracking
  - Logging timestamps
  - Temporary resource naming
Functions Used:
  - datetime.now()
  - strftime()
  - timedelta
```

### 2. OS Module
```yaml
Module: os
Purpose: Operating system interface
Usage:
  - Environment variable access
  - File path operations
  - System information retrieval
Functions Used:
  - os.environ.get()
  - os.path.join()
  - os.path.exists()
```

### 3. Tempfile Module
```yaml
Module: tempfile
Purpose: Temporary file and directory creation
Usage:
  - Temporary file handling
  - Secure temporary storage
  - Cleanup management
Functions Used:
  - tempfile.NamedTemporaryFile()
  - tempfile.mkdtemp()
```

## Optional Dependencies

### 1. Development Dependencies
```yaml
Package: pytest
Version: >= 7.0.0
Purpose: Testing framework
Usage: Unit and integration testing

Package: black
Version: >= 23.0.0
Purpose: Code formatting
Usage: Consistent code style

Package: flake8
Version: >= 6.0.0
Purpose: Linting
Usage: Code quality checks

Package: mypy
Version: >= 1.0.0
Purpose: Static type checking
Usage: Type safety validation
```

### 2. Monitoring Dependencies
```yaml
Package: structlog
Version: >= 23.0.0
Purpose: Structured logging
Usage: Application logging and monitoring

Package: prometheus-client
Version: >= 0.17.0
Purpose: Metrics collection
Usage: Performance monitoring
```

## Package Configuration

### 1. Requirements.txt
```txt
# Core dependencies
streamlit>=1.28.0
snowflake-snowpark-python>=1.8.0
snowflake-connector-python>=3.0.0

# Development dependencies
pytest>=7.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0

# Optional monitoring
structlog>=23.0.0
prometheus-client>=0.17.0
```

### 2. Setup.py Configuration
```python
from setuptools import setup, find_packages

setup(
    name="svg-image-generator",
    version="1.0.0",
    description="SVG Image Generation with Snowflake Cortex",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "snowflake-snowpark-python>=1.8.0",
        "snowflake-connector-python>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "monitoring": [
            "structlog>=23.0.0",
            "prometheus-client>=0.17.0",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
```

### 3. Pyproject.toml Configuration
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "svg-image-generator"
version = "1.0.0"
description = "SVG Image Generation with Snowflake Cortex"
authors = [{name = "Your Name", email = "your.email@example.com"}]
license = {text = "MIT"}
readme = "README.md"
requires-python = ">=3.8"
dependencies = [
    "streamlit>=1.28.0",
    "snowflake-snowpark-python>=1.8.0",
    "snowflake-connector-python>=3.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]
monitoring = [
    "structlog>=23.0.0",
    "prometheus-client>=0.17.0",
]

[tool.black]
line-length = 88
target-version = ['py38']

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

## Dependency Management

### 1. Version Pinning Strategy
```yaml
Version Strategy:
  - Core dependencies: Pinned to specific versions
  - Development dependencies: Minimum version requirements
  - Security updates: Automatic updates for patch versions
  - Breaking changes: Manual review and testing required
```

### 2. Security Considerations
```yaml
Security Measures:
  - Regular dependency updates
  - Vulnerability scanning
  - License compliance checking
  - Supply chain security
  - Dependency pinning for reproducible builds
```

### 3. Compatibility Matrix
```yaml
Python Versions:
  - 3.8: Fully supported
  - 3.9: Fully supported
  - 3.10: Fully supported
  - 3.11: Fully supported
  - 3.12: Testing in progress

Operating Systems:
  - Linux: Fully supported
  - macOS: Fully supported
  - Windows: Limited support (Snowflake connector issues)

Snowflake Versions:
  - Enterprise: Fully supported
  - Standard: Fully supported
  - VPS: Limited support
```

## Package Usage Patterns

### 1. Streamlit Usage
```python
# Page configuration
st.set_page_config(
    page_title="SVG Generator with Snowflake Cortex",
    page_icon="🎨",
    layout="wide"
)

# Session state management
@st.cache_resource
def get_session():
    return get_active_session()

# UI components
st.title("🎨 SVG Generator with Snowflake Cortex")
st.sidebar.header("Configuration")
st.text_area("Describe the SVG you want to generate:")
st.selectbox("Cortex Model:", model_options)
st.button("Generate SVG and Upload to Stage", type="primary")
```

### 2. Snowpark Usage
```python
# Session management
session = get_active_session()

# SQL execution
result = session.sql(cortex_query).collect()

# Stage operations
session.sql(f"CREATE STAGE IF NOT EXISTS {stage_name}").collect()
session.sql(f"LIST @{stage_name}").collect()

# Table operations
session.sql(f"CREATE TRANSIENT TABLE {temp_table}").collect()
session.sql(f"INSERT INTO {temp_table} SELECT $${svg_content}$$").collect()
```

### 3. Error Handling Patterns
```python
try:
    session = get_session()
    st.success("✅ Connected to Snowflake using active session")
except Exception as e:
    st.error(f"❌ Failed to get active session: {str(e)}")
    st.stop()

try:
    result = session.sql(cortex_query).collect()
    svg_content = result[0][0] if result else None
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    with st.expander("Error Details"):
        st.write(str(e))
```

## Performance Optimization

### 1. Caching Strategies
```python
# Session caching
@st.cache_resource
def get_session():
    return get_active_session()

# Data caching
@st.cache_data(ttl=3600)
def get_stage_contents(stage_name):
    return session.sql(f"LIST @{stage_name}").collect()
```

### 2. Resource Management
```python
# Automatic cleanup
try:
    # Create temporary resources
    session.sql(f"CREATE TRANSIENT TABLE {temp_table}").collect()
    # ... operations ...
finally:
    # Cleanup
    session.sql(f"DROP TABLE IF EXISTS {temp_table}").collect()
```

### 3. Memory Management
```yaml
Memory Optimization:
  - Use transient tables for temporary data
  - Implement proper cleanup procedures
  - Limit result set sizes
  - Use streaming for large files
```

## Deployment Considerations

### 1. Environment Variables
```bash
# Required environment variables
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# Optional environment variables
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_SERVER_HEADLESS=true
```

### 2. Container Configuration
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "SVG-Image-Gen.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 3. Runtime Configuration
```yaml
Runtime Settings:
  - Python version: 3.9+
  - Memory: 2GB minimum, 4GB recommended
  - CPU: 2 cores minimum, 4 cores recommended
  - Storage: 10GB minimum for temporary files
  - Network: HTTPS access to Snowflake APIs
``` 