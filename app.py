#!/usr/bin/env python3
"""
Railway deployment entry point
"""

import os
import sys

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the Flask app from backend
if __name__ == '__main__':
    from backend.app import app
    
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting server on port {port}")
    print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
