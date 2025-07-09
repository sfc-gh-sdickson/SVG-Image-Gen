# 🎨 Live UIStateManager Observability Demo

This demo provides **real-time state management** with actual Python backend using the best available HTML5 facilities: **Server-Sent Events (SSE)** for real-time updates and **REST API** for state management.

## 🚀 Quick Start

### 1. Start the Python API Server
```bash
# Activate virtual environment
source .venv/bin/activate

# Start the FastAPI server
python start_state_api.py
```

The server will start at `http://127.0.0.1:8000`

### 2. Access the Live Dashboard
- **Option A**: Visit `http://127.0.0.1:8000` directly (served by FastAPI)
- **Option B**: Use Live Server extension on `ui_observability_demo.html`

## 📊 Features

### Real-Time State Management
- **Live Connection Status**: Visual indicator showing API connection state
- **Real-Time Updates**: State changes appear instantly via Server-Sent Events
- **Actual Python Backend**: Uses the real UIStateManager, not mock data
- **Structured Logging**: All state changes logged with rich context

### Interactive Controls
- **Form Data Management**: Update form fields and see real-time state changes
- **Step Transitions**: Navigate through UI states (setup → form_fill → validation → generation → complete)
- **Loading States**: Simulate loading states for different components
- **Validation Errors**: Add and clear validation errors with detailed logging
- **State Management**: Reset state and log comprehensive summaries

### Observability Dashboard
- **Live State Display**: Current state values update in real-time
- **Structured Logging**: View detailed logs with timestamps, levels, and context
- **Connection Status**: Visual feedback for API connectivity
- **Error Handling**: Graceful handling of connection issues

## 🛠️ Technical Implementation

### Backend (Python/FastAPI)
- **FastAPI Server**: REST API endpoints for state management
- **Server-Sent Events**: Real-time state updates to HTML clients
- **UIStateManager Integration**: Uses the actual Python state manager
- **CORS Support**: Allows cross-origin requests from HTML clients

### Frontend (HTML5/JavaScript)
- **Server-Sent Events**: Real-time updates using `EventSource`
- **Fetch API**: REST calls for state management
- **Connection Management**: Automatic reconnection and error handling
- **Responsive Design**: Modern CSS with gradient styling

### API Endpoints
```
GET  /api/health          - Health check
GET  /api/state           - Get current state
POST /api/state/step      - Set current step
POST /api/state/form      - Update form data
POST /api/state/loading   - Set loading state
POST /api/state/validation-error - Add validation error
DELETE /api/state/validation-errors - Clear all errors
POST /api/state/reset     - Reset all state
GET  /api/events          - Server-Sent Events stream
```

## 🎯 Usage Examples

### Basic State Management
```javascript
// Update form data
await fetch('http://127.0.0.1:8000/api/state/form', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: "Create a blue circle",
        model: "claude-3-5-sonnet",
        size: "512x512"
    })
});

// Change current step
await fetch('http://127.0.0.1:8000/api/state/step', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ step: "validation" })
});
```

### Real-Time Updates
```javascript
// Connect to Server-Sent Events
const eventSource = new EventSource('http://127.0.0.1:8000/api/events');

eventSource.onmessage = function(event) {
    const update = JSON.parse(event.data);
    console.log('State update:', update);
    // Update UI based on state change
};
```

## 🔧 Development

### Project Structure
```
├── src/svg_image_generator/
│   ├── ui_state_manager.py    # Core state management
│   ├── state_api.py          # FastAPI server
│   └── llm_logging.py        # Structured logging
├── ui_observability_demo.html # Live dashboard
├── start_state_api.py        # Server startup script
└── README_live_demo.md       # This file
```

### Adding New State Features
1. **Backend**: Add methods to `UIStateManager` class
2. **API**: Add endpoints to `state_api.py`
3. **Frontend**: Add controls to HTML dashboard
4. **Testing**: Use the live dashboard to verify functionality

### Customization
- **API URL**: Change `API_BASE_URL` in HTML file
- **Port**: Modify port in `start_state_api.py`
- **Styling**: Update CSS in HTML file
- **Logging**: Configure logging levels in `llm_logging.py`

## 🐛 Troubleshooting

### Connection Issues
- **Check server**: Ensure `python start_state_api.py` is running
- **Check port**: Verify server is on port 8000
- **Check CORS**: Ensure browser allows cross-origin requests
- **Check logs**: Look for error messages in browser console

### State Not Updating
- **Check EventSource**: Verify SSE connection in browser dev tools
- **Check API calls**: Ensure fetch requests are successful
- **Check state manager**: Verify Python state manager is working

### Performance Issues
- **Reduce polling**: Adjust reconnection intervals
- **Optimize logging**: Reduce log verbosity if needed
- **Monitor memory**: Check for memory leaks in long-running sessions

## 📈 Benefits

### For Developers
- **Real-Time Debugging**: See state changes as they happen
- **API Testing**: Test state management endpoints interactively
- **Integration Testing**: Verify frontend-backend communication
- **Documentation**: Self-documenting state transitions

### For Users
- **Transparency**: Clear visibility into application state
- **Feedback**: Immediate response to all actions
- **Error Recovery**: Clear error messages and recovery options
- **Progress Tracking**: Visual progress through workflow steps

## 🔗 Integration with Main App

This demo can be integrated with your main Streamlit application:

1. **Replace Mock State**: Use the real UIStateManager in your Streamlit app
2. **Add API Endpoints**: Expose state via FastAPI endpoints
3. **Connect Dashboard**: Point the HTML dashboard to your app's API
4. **Add Observability**: Use the structured logging in your main app

## 🎨 Design Principles

### User Experience
- **Progressive Disclosure**: Show only relevant controls based on current state
- **Visual Feedback**: Immediate visual response to all actions
- **Error Handling**: Clear error states and recovery options
- **Loading States**: Visual indicators for async operations

### Observability
- **Comprehensive Logging**: Every state change is logged with context
- **Structured Data**: JSON-formatted context for easy parsing
- **Timeline Tracking**: Complete audit trail of user interactions
- **Debug Information**: Rich context for troubleshooting

## 🚀 Next Steps

1. **Integrate with Streamlit**: Connect the dashboard to your main app
2. **Add Authentication**: Secure the API endpoints
3. **Add Persistence**: Save state to database
4. **Add Analytics**: Track usage patterns and performance
5. **Add Customization**: Allow users to customize the dashboard

---

**🎯 Result**: A truly "live" dashboard that reflects the actual state of your Python application using the best available HTML5 facilities!
