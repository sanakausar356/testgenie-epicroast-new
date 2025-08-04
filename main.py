#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""

import sys
import os

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
try:
    from backend.app import app
    print("✅ Successfully imported full backend app")
except Exception as e:
    print(f"Error importing full backend app: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Create a minimal Flask app as fallback
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running (fallback mode)',
            'services': {
                'testgenie': False,
                'epicroast': False,
                'groomroom': False,
                'jira': False
            }
        })
    
    @app.route('/api/health', methods=['GET'])
    def api_health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running (fallback mode)',
            'services': {
                'testgenie': False,
                'epicroast': False,
                'groomroom': False,
                'jira': False
            }
        })

    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'TestGenie & Epic Roast API (Fallback Mode)',
            'version': '1.0.0',
            'status': 'Backend is running but services are not configured',
            'endpoints': {
                'health': '/health',
                'api_health': '/api/health'
            }
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port) 