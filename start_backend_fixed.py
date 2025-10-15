#!/usr/bin/env python3
"""
Fixed backend startup script
"""

import os
import sys
from pathlib import Path

def main():
    """Start the backend with proper path handling"""
    print("🚀 Starting TestGenie Backend...")
    
    # Set environment variables
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    os.environ['PORT'] = '5000'
    
    # Add current directory and backend directory to Python path
    current_dir = Path(__file__).parent
    backend_dir = current_dir / "backend"
    
    sys.path.insert(0, str(current_dir))
    sys.path.insert(0, str(backend_dir))
    
    print("✅ Environment configured")
    print("🌐 Backend will be available at: http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("🔧 Press Ctrl+C to stop the server")
    
    try:
        # Change to backend directory and import
        os.chdir(backend_dir)
        from app import app
        
        print("✅ Flask app imported successfully")
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Trying alternative import method...")
        
        try:
            # Try importing directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("app", backend_dir / "app.py")
            app_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(app_module)
            app = app_module.app
            
            print("✅ Flask app imported via alternative method")
            app.run(host='0.0.0.0', port=5000, debug=True)
            
        except Exception as e2:
            print(f"❌ Alternative import failed: {e2}")
            print("Please check that all dependencies are installed:")
            print("pip install -r requirements.txt")
            return False
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return False

if __name__ == "__main__":
    main()
