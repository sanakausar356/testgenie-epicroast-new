#!/usr/bin/env python3
"""
Start TestGenie Backend Locally
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup basic environment variables"""
    env_vars = {
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': 'True',
        'PORT': '5000'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")

def start_backend():
    """Start the Flask backend"""
    print("🚀 Starting TestGenie Backend...")
    
    # Setup environment
    setup_environment()
    
    # Change to backend directory
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    os.chdir(backend_dir)
    
    # Add parent directory to Python path
    sys.path.append(str(Path("..")))
    
    print("✅ Backend environment configured")
    print("🌐 Backend will be available at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("🔧 Press Ctrl+C to stop the server")
    
    # Import and run the Flask app
    try:
        # Import from the current directory (backend)
        import app
        app = app.app
        app.run(host='0.0.0.0', port=5000, debug=True)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

if __name__ == "__main__":
    start_backend()
