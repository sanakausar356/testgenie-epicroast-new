#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""

import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the Flask app
try:
    from app import app
    print("✅ Successfully imported full backend app")
except Exception as e:
    print(f"Error importing full backend app: {e}")
    # Create a minimal Flask app as fallback
    from flask import Flask, jsonify, request
    app = Flask(__name__)
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Backend is running (fallback mode)',
            'services': {
                'testgenie': False,
                'epicroast': False,
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
    app.run(host='0.0.0.0', port=port) 