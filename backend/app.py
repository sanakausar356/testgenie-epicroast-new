#!/usr/bin/env python3
"""
TestGenie & EpicRoast Web API
Flask backend for the web interface
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import sys

# Add parent directory to path to import existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testgenie.core import TestGenie
from epicroast.core import EpicRoast
from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize core services
testgenie = TestGenie()
epicroast = EpicRoast()
jira_integration = JiraIntegration()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'testgenie': testgenie.client is not None,
            'epicroast': epicroast.client is not None,
            'jira': jira_integration.is_available()
        }
    })

@app.route('/api/jira/ticket/<ticket_number>', methods=['GET'])
def get_jira_ticket(ticket_number):
    """Get Jira ticket information"""
    try:
        ticket_info = jira_integration.get_ticket_info(ticket_number)
        if ticket_info:
            return jsonify({
                'success': True,
                'data': ticket_info
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Ticket {ticket_number} not found or access denied'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/testgenie/generate', methods=['POST'])
def generate_test_scenarios():
    """Generate test scenarios from acceptance criteria"""
    try:
        data = request.get_json()
        acceptance_criteria = data.get('acceptance_criteria', '')
        ticket_number = data.get('ticket_number', '')
        
        if not acceptance_criteria and not ticket_number:
            return jsonify({
                'success': False,
                'error': 'Either acceptance_criteria or ticket_number must be provided'
            }), 400
        
        # Get acceptance criteria from Jira if ticket number provided
        if ticket_number and not acceptance_criteria:
            ticket_info = jira_integration.get_ticket_info(ticket_number)
            if ticket_info:
                acceptance_criteria = jira_integration.format_ticket_for_analysis(ticket_info)
            else:
                return jsonify({
                    'success': False,
                    'error': f'Could not fetch ticket {ticket_number}'
                }), 404
        
        # Generate test scenarios
        scenarios = testgenie.generate_test_scenarios(acceptance_criteria, scenario_types=['positive', 'negative', 'edge'])
        
        return jsonify({
            'success': True,
            'data': {
                'scenarios': scenarios,
                'ticket_number': ticket_number if ticket_number else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/epicroast/generate', methods=['POST'])
def generate_roast():
    """Generate roast from ticket content"""
    try:
        data = request.get_json()
        ticket_content = data.get('ticket_content', '')
        ticket_number = data.get('ticket_number', '')
        theme = data.get('theme', 'default')
        level = data.get('level', 'savage')
        
        if not ticket_content and not ticket_number:
            return jsonify({
                'success': False,
                'error': 'Either ticket_content or ticket_number must be provided'
            }), 400
        
        # Get ticket content from Jira if ticket number provided
        if ticket_number and not ticket_content:
            ticket_info = jira_integration.get_ticket_info(ticket_number)
            if ticket_info:
                ticket_content = jira_integration.format_ticket_for_analysis(ticket_info)
            else:
                return jsonify({
                    'success': False,
                    'error': f'Could not fetch ticket {ticket_number}'
                }), 404
        
        # Generate roast
        roast = epicroast.generate_roast(ticket_content, theme=theme, level=level)
        
        return jsonify({
            'success': True,
            'data': {
                'roast': roast,
                'theme': theme,
                'level': level,
                'ticket_number': ticket_number if ticket_number else None
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/teams/share', methods=['POST'])
def share_to_teams():
    """Generate Teams shareable content"""
    try:
        data = request.get_json()
        content_type = data.get('type')  # 'testgenie' or 'epicroast'
        content = data.get('content', '')
        ticket_number = data.get('ticket_number', '')
        
        if content_type == 'testgenie':
            teams_message = f"""
🎯 **TestGenie Results** {f'for {ticket_number}' if ticket_number else ''}

{content[:500]}{'...' if len(content) > 500 else ''}

*Generated by TestGenie Web App*
            """.strip()
        else:  # epicroast
            teams_message = f"""
🔥 **Epic Roast** {f'of {ticket_number}' if ticket_number else ''}

{content[:500]}{'...' if len(content) > 500 else ''}

*Generated by Epic Roast Web App*
            """.strip()
        
        return jsonify({
            'success': True,
            'data': {
                'teams_message': teams_message,
                'copy_text': content
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 