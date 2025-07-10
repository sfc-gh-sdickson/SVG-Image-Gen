# Project Structure

## Entry Points

### Main Streamlit App
- **File**: `SVG-Image-Gen.py` (root directory)
- **Purpose**: Main Streamlit application for SVG generation
- **Run**: `streamlit run SVG-Image-Gen.py`
- **Entry Point**: `streamlit-app` (via pyproject.toml)

### Development Tools
- **File**: `src/svg_image_generator/app.py`
- **Purpose**: Development/testing version of the app
- **Run**: `streamlit run src/svg_image_generator/app.py`

### CLI Tools
- **File**: `src/svg_image_generator/cli.py`
- **Purpose**: Command-line interface tools
- **Run**: `svg-generator` (via pyproject.toml entry point)

## Project Layout

```
SVG-Image-Gen/
├── SVG-Image-Gen.py          # Main Streamlit app (production)
├── src/svg_image_generator/  # Source package
│   ├── app.py               # Development version
│   ├── cli.py               # CLI tools
│   └── ...
├── tests/                   # Test suite
├── ontologies/              # Ontology definitions
├── models/                  # Data models
└── pyproject.toml          # Project metadata & entry points
```

## Runtime Detection

The main app (`SVG-Image-Gen.py`) includes runtime detection:
- Detects when run directly vs imported as module
- Provides clear entry point identification
- Supports both direct execution and package installation

## Tooling Support

### Entry Points (pyproject.toml)
- `streamlit-app`: Points to main app
- `svg-generator`: CLI tools
- `svg-generator-gui`: GUI tools (if implemented)

### Development Workflow
1. **Local Development**: Use `src/svg_image_generator/app.py`
2. **Production**: Use `SVG-Image-Gen.py`
3. **Testing**: Use `pytest` with proper test discovery
4. **CLI Tools**: Use `svg-generator` command

## Why This Structure?

- **Clear Entry Point**: `SVG-Image-Gen.py` is obviously the main app
- **Tooling Support**: pyproject.toml provides proper entry points
- **Development Flexibility**: Separate dev version for testing
- **Runtime Awareness**: App knows how it's being executed
- **No Proxy Weirdness**: Direct file execution, no complex imports
