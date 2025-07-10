# Streamlit State Management Integration Guide

This guide explains how to integrate the decorator-based state management system with your Streamlit applications for enhanced observability and debugging.

## Quick Start

### 1. Basic Integration

```python
import streamlit as st
from src.svg_image_generator.streamlit_integration import get_state_manager

# Initialize state manager
state_manager = get_state_manager()

# Your existing Streamlit code...
```

### 2. Add Decorators to Existing Functions

```python
from src.svg_image_generator.streamlit_integration import track_step, track_loading

@track_step("form_submission")
def handle_form_submit():
    # Your existing form handling logic
    st.success("Form submitted!")

@track_loading("api_call")
def call_external_api():
    # Your existing API call logic
    time.sleep(2)
    return {"result": "success"}
```

## Decorator Reference

### Step Tracking

Track workflow steps and transitions:

```python
@track_step("step_name")
def your_function():
    # Function logic here
    pass
```

**Usage Examples:**
- `@track_step("form_fill")` - Track form filling step
- `@track_step("validation")` - Track validation step
- `@track_step("generation")` - Track SVG generation step

### Loading State Tracking

Track loading states for components:

```python
@track_loading("component_name", auto_clear=True)
def your_function():
    # Function logic here
    pass
```

**Usage Examples:**
- `@track_loading("cortex_call")` - Track Cortex API calls
- `@track_loading("svg_generation")` - Track SVG generation
- `@track_loading("validation", auto_clear=False)` - Manual control

### Form Data Tracking

Automatically track form data from Streamlit session state:

```python
@track_form_data("form_key")
def process_form():
    # Form processing logic
    pass
```

**Usage Examples:**
- `@track_form_data()` - Track default "form_data" key
- `@track_form_data("user_inputs")` - Track custom form key

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

## Context Managers

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

## Manual State Updates

For complex workflows or custom state management:

```python
# Update multiple state aspects at once
state_manager.manual_state_update(
    step="processing",
    loading_states={"api_call": True, "generation": False},
    form_data={"user_input": "value"}
)

# Update individual aspects
state_manager.manual_state_update(step="complete")
state_manager.manual_state_update(loading_states={"processing": False})
```

## Integration Patterns

### Pattern 1: Minimal Integration

Add decorators to existing functions without changing logic:

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

Wrap existing code blocks with context managers:

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

Start with basic tracking and expand:

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

## API Integration

### Enable/Disable API Sync

```python
# Disable API sync for testing
state_manager.enable_api_sync(False)

# Re-enable for production
state_manager.enable_api_sync(True)
```

### Custom API URL

```python
# Use custom API server
state_manager = get_state_manager("http://your-api-server:8000")
```

## Debugging and Monitoring

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

## Best Practices

### 1. Granular Step Tracking

Break workflows into meaningful steps:

```python
@track_step("initialization")
def initialize():
    pass

@track_step("data_loading")
def load_data():
    pass

@track_step("processing")
def process():
    pass

@track_step("completion")
def complete():
    pass
```

### 2. Descriptive Component Names

Use clear, descriptive names for loading states:

```python
@track_loading("cortex_api_call")
@track_loading("svg_generation")
@track_loading("validation_check")
```

### 3. Error Handling

Context managers automatically handle cleanup:

```python
with loading_context("api_call"):
    try:
        # API call logic
        pass
    except Exception as e:
        # Loading state automatically cleared
        raise
```

### 4. Form Data Consistency

Use consistent form keys:

```python
@track_form_data("user_inputs")
def handle_user_input():
    # Form logic
    pass
```

## Migration Guide

### From Manual State Management

**Before:**
```python
def handle_form():
    st.session_state["current_step"] = "form_handling"
    st.session_state["loading"] = True
    try:
        # Form logic
        pass
    finally:
        st.session_state["loading"] = False
```

**After:**
```python
@track_step("form_handling")
@track_loading("form_processing")
def handle_form():
    # Same form logic
    pass
```

### From Custom Logging

**Before:**
```python
def api_call():
    logger.info("Starting API call")
    # API logic
    logger.info("API call completed")
```

**After:**
```python
@track_loading("api_call")
def api_call():
    # Same API logic
    # Logging handled automatically
```

## Troubleshooting

### Common Issues

1. **Decorator not working**: Ensure you're using the correct import path
2. **API sync failing**: Check if the API server is running
3. **State not updating**: Verify the decorator is applied to the correct function

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check state manager status
print(f"API sync enabled: {state_manager._enabled}")
print(f"Current state: {state_manager.get_current_state()}")
```

## Advanced Usage

### Custom State Extensions

```python
class CustomStateManager(StreamlitStateManager):
    def track_custom_metric(self, metric_name: str):
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

### Integration with External Systems

```python
# Integrate with external monitoring
@track_loading("external_api")
def call_external_api():
    # Your API call
    # State automatically tracked
    pass
```

This integration system provides a clean, decorator-based approach to adding comprehensive state management to your Streamlit applications with minimal code changes.
