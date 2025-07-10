#!/usr/bin/env python3
"""
Test script for Server-Sent Events (SSE) functionality.
"""

import json
import time

import requests


def test_sse_connection():
    """Test SSE connection and receive events."""
    print("🔗 Testing SSE connection...")

    # Start SSE connection
    response = requests.get(
        "http://127.0.0.1:8000/api/events",
        stream=True,
        headers={"Accept": "text/event-stream"},
    )

    if response.status_code != 200:
        print(f"❌ SSE connection failed: {response.status_code}")
        return

    print("✅ SSE connection established")
    print("📡 Listening for events...")
    print("   (Press Ctrl+C to stop)")

    try:
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]  # Remove 'data: ' prefix
                    try:
                        event = json.loads(data)
                        print(f"📨 Event received: {json.dumps(event, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"⚠️  Invalid JSON: {data}")
    except KeyboardInterrupt:
        print("\n👋 SSE test stopped")


def test_state_changes():
    """Test state changes and verify SSE events."""
    print("\n🧪 Testing state changes...")

    # Test step change
    print("1. Changing step to 'validation'...")
    response = requests.post(
        "http://127.0.0.1:8000/api/state/step", json={"step": "validation"}
    )
    print(f"   Response: {response.json()}")

    # Test form data update
    print("2. Updating form data...")
    response = requests.post(
        "http://127.0.0.1:8000/api/state/form",
        json={
            "prompt": "Create a red square",
            "model": "claude-3-7-sonnet",
            "size": "1024x1024",
        },
    )
    print(f"   Response: {response.json()}")

    # Test loading state
    print("3. Setting loading state...")
    response = requests.post(
        "http://127.0.0.1:8000/api/state/loading",
        json={"component": "svg_generation", "is_loading": True},
    )
    print(f"   Response: {response.json()}")

    # Test validation error
    print("4. Adding validation error...")
    response = requests.post(
        "http://127.0.0.1:8000/api/state/validation-error",
        json={"field": "prompt", "message": "Prompt too vague"},
    )
    print(f"   Response: {response.json()}")

    # Check final state
    print("5. Checking final state...")
    response = requests.get("http://127.0.0.1:8000/api/state")
    print(f"   Final state: {json.dumps(response.json(), indent=2)}")


if __name__ == "__main__":
    print("🚀 UIStateManager API Test Suite")
    print("=" * 40)

    # Test basic API functionality
    test_state_changes()

    print("\n" + "=" * 40)
    print("📡 Starting SSE test (will run for 30 seconds)...")

    # Test SSE in background
    import threading
    import time

    def run_sse_test():
        time.sleep(2)  # Wait for connection
        # Make some state changes to trigger events
        requests.post(
            "http://127.0.0.1:8000/api/state/step", json={"step": "generation"}
        )
        time.sleep(1)
        requests.post(
            "http://127.0.0.1:8000/api/state/loading",
            json={"component": "test", "is_loading": True},
        )
        time.sleep(1)
        requests.post(
            "http://127.0.0.1:8000/api/state/loading",
            json={"component": "test", "is_loading": False},
        )

    # Start background thread for state changes
    thread = threading.Thread(target=run_sse_test)
    thread.daemon = True
    thread.start()

    # Run SSE test
    test_sse_connection()
