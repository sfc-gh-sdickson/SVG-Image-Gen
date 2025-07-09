#!/usr/bin/env python3
"""
Start the FastAPI state server for UIStateManager observability demo.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from svg_image_generator.state_api import start_server

if __name__ == "__main__":
    print("🚀 Starting UIStateManager API Server...")
    print("📊 Dashboard will be available at: http://127.0.0.1:8000")
    print("🔗 API endpoints available at: http://127.0.0.1:8000/docs")
    print("📝 Press Ctrl+C to stop the server")
    print()

    try:
        start_server(host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)
