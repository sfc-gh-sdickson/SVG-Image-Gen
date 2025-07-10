# Streamlit State Management Integration

A comprehensive decorator-based state management system for Streamlit applications with real-time observability and debugging capabilities.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install API server dependencies
pip install -r requirements-api.txt

# Or use uv
uv pip install -r requirements-api.txt
```

### 2. Start the State API Server

```bash
# Option 1: Local development
python start_state_api.py

# Option 2: Using deployment script
./scripts/deploy_state_api.sh local

# Option 3: Docker Compose (recommended)
./scripts/deploy_state_api.sh compose
```

### 3. Integrate with Your Streamlit App

```python
import streamlit as st
from src.svg_image_generator.streamlit_integration import track_step, track_loading

@track_step("form_submission")
@track_loading("api_call")
def handle_form_submit():
    # Your existing Streamlit logic
    st.success("Form submitted!")
```

## 🎯 Key Features

### ✅ Decorator-Based Integration
- **Minimal code changes** - Add decorators to existing functions
- **Automatic state tracking** - No manual state management required
- **Backward compatible** - Works with existing Streamlit apps

### ✅ Real-Time Observability
- **Live dashboard** - Monitor state changes in real-time
- **Structured logging** - LLM-friendly logging with context
- **API integration** - REST API for external monitoring

### ✅ Multiple Deployment Options
- **Local development** - Simple Python server
- **Docker deployment** - Containerized for production
- **SiS compatibility** - Separate process architecture
- **Snowflake ready** - Lightweight container support

## 📋 Decorator Reference

### Step Tracking
Track workflow steps and transitions:

```python
@track_step("step_name")
def your_function():
    # Function logic here
    pass
```

**Examples:**
- `@track_step("form_fill")` - Track form filling
- `@track_step("validation")` - Track validation
- `@track_step("generation")` - Track SVG generation

### Loading State Tracking
Track loading states for components:

```python
@track_loading("component_name", auto_clear=True)
def your_function():
    # Function logic here
    pass
```

**Examples:**
- `@track_loading("cortex_call")` - Track API calls
- `@track_loading("svg_generation")` - Track generation
- `@track_loading("validation", auto_clear=False)` - Manual control

### Form Data Tracking
Automatically track form data from Streamlit session state:

```python
@track_form_data("form_key")
def process_form():
    # Form processing logic
    pass
```

### Validation Error Tracking
Track validation errors automatically:

```python
@track_validation_errors("error_key")
def validate_form():
    errors = {}
    # Validation logic
    st.session_state["error_key"] = errors
    return len(errors) == 0
```

## 🔧 Context Managers

### Loading Context
```python
from src.svg_image_generator.streamlit_integration import loading_context

with loading_context("component_name"):
    # Your loading logic here
    time.sleep(2)
```

### Step Context
```python
from src.svg_image_generator.streamlit_integration import step_context

with step_context("step_name"):
    # Your step logic here
    pass
```

## 🚀 Deployment Options

### 1. Local Development
```bash
# Start API server
python start_state_api.py

# Run your Streamlit app
streamlit run your_app.py
```

### 2. Docker Compose (Recommended)
```bash
# Deploy with Docker Compose
./scripts/deploy_state_api.sh compose

# Check status
./scripts/deploy_state_api.sh status

# View logs
./scripts/deploy_state_api.sh logs
```

### 3. Docker Only
```bash
# Deploy with Docker
./scripts/deploy_state_api.sh docker

# Stop services
./scripts/deploy_state_api.sh stop
```

### 4. Snowflake Deployment
```bash
# For Snowflake environments
./scripts/deploy_state_api.sh snowflake
```

## 📊 Dashboard Features

### Real-Time State Display
- **Current step** - Active workflow step
- **Loading states** - Component loading status
- **Form data** - Current form inputs
- **Validation errors** - Form validation issues

### Live Logging
- **Structured logs** - LLM-friendly format
- **Context tracking** - User actions and system state
- **Error visibility** - Clear error messages and context

### API Endpoints
- `GET /api/state` - Get current state
- `POST /api/state/step` - Update step
- `POST /api/state/loading` - Update loading state
- `POST /api/state/form` - Update form data
- `POST /api/state/validation-error` - Add validation error

## 🔄 Integration Patterns

### Pattern 1: Minimal Integration
Add decorators to existing functions:

```python
# Before
def handle_form():
    # Existing logic
    pass

# After
@track_step("form_handling")
@track_form_data()
def handle_form():
    # Same existing logic
    pass
```

### Pattern 2: Context Manager Integration
Wrap existing code blocks:

```python
# Before
def generate_svg():
    st.info("Generating...")
    # SVG generation logic
    st.success("Done!")

# After
def generate_svg():
    with loading_context("svg_generation"):
        with step_context("generation"):
            st.info("Generating...")
            # Same SVG generation logic
            st.success("Done!")
```

### Pattern 3: Progressive Integration
Start simple and expand:

```python
# Phase 1: Basic step tracking
@track_step("main_workflow")
def main_workflow():
    # Your workflow logic
    pass

# Phase 2: Add loading states
@track_step("main_workflow")
def main_workflow():
    with loading_context("data_loading"):
        # Data loading logic

    with loading_context("processing"):
        # Processing logic

# Phase 3: Add form tracking
@track_step("main_workflow")
@track_form_data()
def main_workflow():
    # Enhanced workflow with form tracking
    pass
```

## 🛠️ Configuration

### API Server Configuration
```python
# Custom API URL
state_manager = get_state_manager("http://your-api-server:8000")

# Disable API sync for testing
state_manager.enable_api_sync(False)
```

### Environment Variables
```bash
# API server configuration
API_PORT=8000
DASHBOARD_PORT=80
LOG_LEVEL=INFO
```

## 🔍 Debugging and Monitoring

### View Current State
```python
# Get current state for debugging
current_state = state_manager.get_current_state()
st.json(current_state)
```

### Reset State
```python
# Reset all state to defaults
state_manager.reset_state()
```

### Manual State Updates
```python
# Update multiple state aspects
state_manager.manual_state_update(
    step="processing",
    loading_states={"api_call": True, "generation": False},
    form_data={"user_input": "value"}
)
```

## 📁 Project Structure

```
SVG-Image-Gen/
├── src/svg_image_generator/
│   ├── streamlit_integration.py    # Decorator system
│   ├── ui_state_manager.py         # Core state manager
│   ├── state_api.py               # API server
│   └── llm_logging.py             # Structured logging
├── docker/state-api/
│   ├── Dockerfile                 # Container definition
│   ├── docker-compose.yml         # Multi-service deployment
│   └── nginx.conf                 # Reverse proxy config
├── scripts/
│   └── deploy_state_api.sh        # Deployment script
├── examples/
│   └── streamlit_integration_example.py  # Integration example
├── docs/
│   └── streamlit_integration_guide.md    # Detailed guide
├── requirements-api.txt            # API server dependencies
├── start_state_api.py             # Server startup script
└── README_STATE_INTEGRATION.md    # This file
```

## 🎯 Use Cases

### 1. Form Processing
```python
@track_step("form_processing")
@track_form_data()
@track_validation_errors()
def process_user_form():
    # Form processing logic
    pass
```

### 2. API Integration
```python
@track_loading("cortex_api")
def call_cortex_api():
    # API call logic
    pass
```

### 3. Workflow Management
```python
@track_step("svg_generation")
def generate_svg():
    with loading_context("generation"):
        # SVG generation logic
        pass
```

### 4. Error Handling
```python
@track_validation_errors()
def validate_inputs():
    # Validation logic
    pass
```

## 🔧 Troubleshooting

### Common Issues

1. **Decorator not working**
   - Check import path: `from src.svg_image_generator.streamlit_integration import ...`
   - Verify decorator is applied to correct function

2. **API sync failing**
   - Check if API server is running: `curl http://localhost:8000/health`
   - Verify network connectivity

3. **State not updating**
   - Check if decorator is applied to correct function
   - Verify session state keys match

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check state manager status
print(f"API sync enabled: {state_manager._enabled}")
print(f"Current state: {state_manager.get_current_state()}")
```

## 🚀 Performance Considerations

### Lightweight Design
- **Minimal overhead** - Decorators add minimal performance impact
- **Async API calls** - Non-blocking state synchronization
- **Configurable sync** - Enable/disable API sync as needed

### Scalability
- **Separate process** - API server runs independently
- **Container ready** - Docker deployment for scaling
- **Stateless design** - Easy horizontal scaling

## 🔒 Security

### API Security
- **CORS support** - Configurable cross-origin requests
- **Rate limiting** - Built-in request throttling
- **Health checks** - Automatic health monitoring

### Container Security
- **Non-root user** - Secure container execution
- **Minimal attack surface** - Lightweight base image
- **Regular updates** - Security patch management

## 📈 Monitoring and Observability

### Metrics Available
- **Step transitions** - Workflow progress tracking
- **Loading states** - Component performance monitoring
- **Form interactions** - User engagement metrics
- **Error rates** - Validation and processing errors

### Logging Features
- **Structured logs** - JSON format for easy parsing
- **Context tracking** - User actions and system state
- **Error visibility** - Clear error messages with context
- **LLM-friendly** - Optimized for AI analysis

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd SVG-Image-Gen

# Install dependencies
uv pip install -r requirements-api.txt

# Start development server
python start_state_api.py

# Run tests
make test
```

### Adding New Decorators
```python
# Example: Custom metric tracking
def track_custom_metric(metric_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Custom tracking logic
            result = func(*args, **kwargs)
            # Custom state update
            return result
        return wrapper
    return decorator
```

## 📚 Additional Resources

- [Integration Guide](docs/streamlit_integration_guide.md) - Detailed integration instructions
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Example App](examples/streamlit_integration_example.py) - Complete integration example
- [Deployment Guide](scripts/deploy_state_api.sh) - Deployment instructions

---

This state management system provides a clean, decorator-based approach to adding comprehensive observability to your Streamlit applications with minimal code changes and maximum flexibility for deployment scenarios.
