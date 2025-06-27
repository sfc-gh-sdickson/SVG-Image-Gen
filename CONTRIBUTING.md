# Contributing to SVG Image Generator

Thank you for your interest in contributing to the SVG Image Generator project! This document provides guidelines and workflows for contributors.

## 🚀 Quick Start

1. **Fork and clone** the repository
2. **Set up your development environment** (see [Development Setup](#development-setup))
3. **Create a feature branch** for your changes
4. **Make your changes** following our [coding standards](#coding-standards)
5. **Test your changes** thoroughly
6. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A Snowflake account (for testing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-fork-url>
   cd SVG-Image-Gen
   ```

2. **Install dependencies:**
   ```bash
   # Using pip (recommended for most users)
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Or using uv (faster, more reliable)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv pip install -r requirements.txt
   uv pip install -r requirements-dev.txt
   ```

3. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

4. **Configure environment variables:**
   ```bash
   cp config.example.env .env
   # Edit .env with your Snowflake credentials
   ```

## 🔧 Development Workflow

### Type Checking and Stub Management

We use **mypy** for static type checking. To ensure all dependencies have proper type stubs:

#### Automatic Stub Management

We provide a helper script that automatically detects missing type stubs and adds them to `requirements-dev.txt`:

```bash
# Run the script to detect and fix missing type stubs
python scripts/fix-missing-type-stubs.py
```

This script will:
- Run mypy on your codebase
- Detect missing type stubs
- Add the correct `types-<package>` dependencies to `requirements-dev.txt`
- Optionally install the new stubs

#### Manual Stub Management

If you prefer to handle stubs manually:

1. **Run mypy** to see missing stubs:
   ```bash
   mypy src/
   ```

2. **Add missing stubs** to `requirements-dev.txt`:
   ```txt
   types-requests
   types-PyYAML
   # etc.
   ```

3. **Install the stubs:**
   ```bash
   pip install -r requirements-dev.txt
   ```

### Pre-commit Hooks

Our pre-commit configuration automatically:
- **Fixes missing type stubs** before each commit
- **Formats code** with black and isort
- **Lints code** with ruff and flake8
- **Checks types** with mypy
- **Runs security checks** with bandit

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "unit"      # Unit tests only
pytest -m "integration"  # Integration tests only
pytest -m "snowflake"    # Snowflake-specific tests

# Run with coverage
pytest --cov=src/svg_image_generator --cov-report=html
```

### Code Quality

```bash
# Format code
black src/ tests/
isort src/ tests/

# Lint code
ruff check src/ tests/
flake8 src/ tests/

# Type checking
mypy src/

# Security checks
bandit -r src/
```

## 📝 Coding Standards

### Python Code Style

- **Follow PEP 8** with line length of 88 characters (black default)
- **Use type hints** for all function parameters and return values
- **Write docstrings** for all public functions and classes
- **Use meaningful variable names** and avoid abbreviations

### Example

```python
from typing import Optional, List
from pathlib import Path

def process_svg_files(directory: Path, max_files: Optional[int] = None) -> List[str]:
    """
    Process SVG files in the given directory.

    Args:
        directory: Path to the directory containing SVG files
        max_files: Maximum number of files to process (None for all)

    Returns:
        List of processed file paths

    Raises:
        ValueError: If directory doesn't exist
    """
    if not directory.exists():
        raise ValueError(f"Directory {directory} does not exist")

    svg_files = list(directory.glob("*.svg"))
    if max_files:
        svg_files = svg_files[:max_files]

    return [str(f) for f in svg_files]
```

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(auth): add dual authentication support`
- `fix(pre-commit): remove deprecated yml type from prettier config`
- `docs(readme): add uv installation instructions`
- `test(authentication): add tests for local environment setup`

### Pull Request Guidelines

1. **Create a descriptive title** that summarizes the change
2. **Write a detailed description** explaining what and why
3. **Include tests** for new functionality
4. **Update documentation** if needed
5. **Ensure all checks pass** (CI, pre-commit, tests)

## 🔐 Authentication and Environment

### Local Development

For local development, you need to set up environment variables:

```bash
# Required
SNOWFLAKE_ACCOUNT=your-account-identifier
SNOWFLAKE_USER=your-username
SNOWFLAKE_PASSWORD=your-password
SNOWFLAKE_WAREHOUSE=your-warehouse-name

# Optional
SNOWFLAKE_DATABASE=your-database-name
SNOWFLAKE_SCHEMA=your-schema-name
SNOWFLAKE_ROLE=your-role-name
```

### Streamlit in Snowflake (SiS)

When deployed in Snowflake, the application automatically uses your active session - no additional configuration needed.

## 🧪 Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Snowflake tests**: Test Snowflake-specific functionality

### Test Naming

```python
def test_function_name_with_expected_behavior():
    """Test description of what is being tested."""
    # Arrange
    # Act
    # Assert
```

### Mocking

Use `pytest-mock` for mocking:

```python
def test_function_with_mock(mocker):
    mock_session = mocker.patch('snowflake.snowpark.Session')
    # Test implementation
```

## 🚀 Deployment

### Local Testing

```bash
streamlit run SVG-Image-Gen.py
```

### Production Deployment

1. **Deploy to Streamlit in Snowflake (SiS)**
2. **Configure environment variables** in Snowflake
3. **Test the deployment** thoroughly

## 🤝 Getting Help

- **Check existing issues** before creating new ones
- **Use the discussion forum** for questions and ideas
- **Join our community** for real-time help

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to SVG Image Generator! 🎨
