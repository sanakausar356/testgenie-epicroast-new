#!/usr/bin/env python3
"""
TestGenie & EpicRoast with GroomRoom - Flask Backend API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return jsonify({
        "message": "TestGenie & EpicRoast with GroomRoom API",
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "testgenie": "AI-powered test case generation",
            "epicroast": "Jira ticket roasting and analysis", 
            "groomroom": "Enhanced ticket grooming and analysis"
        }
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "services": {
            "groomroom": True,
            "jira": True,
            "testgenie": True,
            "epicroast": True
        }
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "healthy",
        "message": "API is working",
        "timestamp": "2024-10-19T22:38:00Z"
    })

@app.route('/api/groomroom', methods=['POST'])
def generate_groom():
    """Generate GroomRoom analysis using the actual GroomRoom service"""
    try:
        from groomroom.core import GroomRoom
        
        data = request.get_json()
        ticket_number = data.get('ticket_number', '')
        ticket_content = data.get('ticket_content', '')
        level = data.get('level', 'actionable')
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        
        # Determine input content
        if ticket_number:
            # Use ticket number to fetch from Jira
            content = ticket_number
        else:
            # Use provided content
            content = ticket_content
        
        # Generate analysis
        result = groomroom.analyze_ticket(content, mode=level)
        
        # Format response
        analysis = {
            'groom': result.get('formatted_output', str(result)),
            'level': level,
            'ticket_number': ticket_number,
            'sprint_readiness': result.get('SprintReadiness', 0),
            'type': result.get('Type', 'Unknown'),
            'issues_found': result.get('DefinitionOfReady', {}).get('MissingFields', []),
            'suggestions': result.get('Recommendations', [])
        }
        
        return jsonify({
            'success': True,
            'data': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/testgenie/generate', methods=['POST'])
def generate_tests():
    """Generate test cases using TestGenie"""
    try:
        data = request.get_json()
        acceptance_criteria = data.get('acceptance_criteria', '')
        
        # Placeholder for TestGenie test generation
        test_scenarios = {
            'positive_tests': [],
            'negative_tests': [],
            'edge_cases': []
        }
        
        return jsonify({
            'success': True,
            'data': {
                'test_scenarios': test_scenarios,
                'acceptance_criteria': acceptance_criteria
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/epicroast/roast', methods=['POST'])
def roast_ticket():
    """Generate EpicRoast analysis"""
    try:
        data = request.get_json()
        ticket_content = data.get('ticket_content', '')
        theme = data.get('theme', 'default')
        
        # Placeholder for EpicRoast
        roast = {
            'roast': f"EpicRoast analysis for: {ticket_content[:50]}... (Theme: {theme})",
            'theme': theme,
            'issues_found': [],
            'suggestions': []
        }
        
        return jsonify({
            'success': True,
            'data': roast
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting TestGenie & EpicRoast with GroomRoom API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)