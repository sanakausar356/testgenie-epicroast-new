#!/usr/bin/env python3
"""
Main entry point for Railway deployment
"""

import sys
import os
import logging

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
try:
    from backend.app import app
    logger.info("✅ Successfully imported full backend app")
except Exception as e:
    logger.error(f"Error importing full backend app: {e}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
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
    logger.info(f"🚀 Starting server on port {port}")
    logger.info(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'development')}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1) 