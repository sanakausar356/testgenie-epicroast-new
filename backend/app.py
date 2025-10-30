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
from groomroom.core import GroomRoom
from jira_integration import JiraIntegration

# Load environment variables
load_dotenv()
# Disable proxy settings for Azure OpenAI
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

# Disable proxy settings for Azure OpenAI
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize core services with error handling
testgenie = None
epicroast = None
groomroom = None
jira_integration = None

# Initialize services one by one with detailed error handling
try:
    print("Initializing TestGenie...")
    testgenie = TestGenie()
    print("✅ TestGenie initialized successfully")
except Exception as e:
    print(f"❌ TestGenie initialization failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Initializing EpicRoast...")
    epicroast = EpicRoast()
    print("✅ EpicRoast initialized successfully")
except Exception as e:
    print(f"❌ EpicRoast initialization failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Initializing GroomRoom...")
    groomroom = GroomRoom()
    print("✅ GroomRoom initialized successfully")
except Exception as e:
    print(f"❌ GroomRoom initialization failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("Initializing JiraIntegration...")
    jira_integration = JiraIntegration()
    print("✅ JiraIntegration initialized successfully")
except Exception as e:
    print(f"❌ Jira integration initialization failed: {e}")
    import traceback
    traceback.print_exc()

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'TestGenie & Epic Roast API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'api_health': '/api/health',
            'testgenie': '/api/testgenie/generate',
            'epicroast': '/api/epicroast/generate',
            'groomroom': '/api/groomroom/generate',
            'groomroom_concise': '/api/groomroom/concise',
            'jira_ticket': '/api/jira/ticket/<ticket_number>'
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'testgenie': testgenie.client is not None if testgenie else False,
            'epicroast': epicroast.client is not None if epicroast else False,
            'groomroom': groomroom.client is not None if groomroom else False,
            'jira': jira_integration.is_available() if jira_integration else False
        }
    })

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """Health check endpoint for API"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'testgenie': testgenie.client is not None if testgenie else False,
            'epicroast': epicroast.client is not None if epicroast else False,
            'groomroom': groomroom.client is not None if groomroom else False,
            'jira': jira_integration.is_available() if jira_integration else False
        }
    })

@app.route('/api/jira/ticket/<ticket_number>', methods=['GET'])
def get_jira_ticket(ticket_number):
    """Get Jira ticket information"""
    if not jira_integration:
        return jsonify({
            'success': False,
            'error': 'Jira integration not available'
        }), 503
    
    try:
        ticket_info = jira_integration.get_ticket_info(ticket_number)
        if ticket_info:
            # Return formatted ticket data instead of raw data
            formatted_ticket = {
                'key': ticket_info.get('key', ''),
                'summary': ticket_info.get('summary', ''),
                'description': ticket_info.get('description', 'No description provided'),
                'status': ticket_info.get('status', 'Unknown'),
                'priority': ticket_info.get('priority', 'None'),
                'assignee': ticket_info.get('assignee', 'Unassigned'),
                'reporter': ticket_info.get('reporter', 'Unknown'),
                'created': ticket_info.get('created', ''),
                'updated': ticket_info.get('updated', ''),
                'issue_type': ticket_info.get('issue_type', 'Unknown'),
                'project': ticket_info.get('project', 'Unknown'),
                'labels': ticket_info.get('labels', []),
                'components': ticket_info.get('components', []),
                'comments': ticket_info.get('comments', [])
            }
            return jsonify({
                'success': True,
                'data': formatted_ticket
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
    if not testgenie:
        return jsonify({
            'success': False,
            'error': 'TestGenie service not available'
        }), 503
    
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
            if not jira_integration or not jira_integration.is_available():
                return jsonify({
                    'success': False,
                    'error': 'Jira integration not available'
                }), 503
            
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
    if not epicroast:
        return jsonify({
            'success': False,
            'error': 'EpicRoast service not available'
        }), 503
    
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
            if not jira_integration or not jira_integration.is_available():
                return jsonify({
                    'success': False,
                    'error': 'Jira integration not available'
                }), 503
            
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

@app.route('/api/groomroom/generate', methods=['POST'])
def generate_groom():
    """Generate groom analysis from ticket content"""
    print("=== GROOMROOM API CALL START ===")
    
    if not groomroom:
        print("ERROR: GroomRoom service not available")
        return jsonify({
            'success': False,
            'error': 'GroomRoom service not available'
        }), 503
    
    try:
        data = request.get_json()
        ticket_content = data.get('ticket_content', '')
        ticket_number = data.get('ticket_number', '')
        level = data.get('level', 'default')
        
        print(f"Request data: ticket_content length={len(ticket_content)}, ticket_number={ticket_number}, level={level}")
        
        if not ticket_content and not ticket_number:
            print("ERROR: No ticket content or number provided")
            return jsonify({
                'success': False,
                'error': 'Either ticket_content or ticket_number must be provided'
            }), 400
        
        # Get ticket content from Jira if ticket number provided
        if ticket_number and not ticket_content:
            print(f"Fetching ticket {ticket_number} from Jira...")
            if not jira_integration or not jira_integration.is_available():
                print("ERROR: Jira integration not available")
                return jsonify({
                    'success': False,
                    'error': 'Jira integration not available'
                }), 503
            
            ticket_info = jira_integration.get_ticket_info(ticket_number)
            if ticket_info:
                ticket_content = jira_integration.format_ticket_for_analysis(ticket_info)
                print(f"Successfully fetched ticket content, length={len(ticket_content)}")
            else:
                print(f"ERROR: Could not fetch ticket {ticket_number}")
                return jsonify({
                    'success': False,
                    'error': f'Could not fetch ticket {ticket_number}'
                }), 404
        
        # Check if groomroom client is available
        print(f"GroomRoom client available: {groomroom.client is not None}")
        if not groomroom.client:
            print("ERROR: Azure OpenAI client not configured")
            return jsonify({
                'success': False,
                'error': 'Azure OpenAI client not configured. Please check environment variables.',
                'details': {
                    'endpoint_set': bool(os.getenv('AZURE_OPENAI_ENDPOINT')),
                    'api_key_set': bool(os.getenv('AZURE_OPENAI_API_KEY')),
                    'deployment_set': bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))
                }
            }), 503
        
        # Generate enhanced groom analysis with fallback
        print(f"Calling groomroom analysis with level={level}")
        debug_mode = data.get('debug_mode', False)
        
        # Add request ID for debugging
        import time
        request_id = int(time.time())
        print(f"Request ID: {request_id}")
        print(f"Ticket content preview: {ticket_content[:200]}...")
        
        # Use the new enhanced analyze_ticket method
        try:
            # Get figma_link from request if provided
            figma_link = data.get('figma_link', None)
            
            # Call the enhanced analyze_ticket method
            result = groomroom.analyze_ticket(ticket_content, mode=level, figma_link=figma_link)
            print("Using enhanced analyze_ticket method")
            
            # Handle the enhanced result structure
            if isinstance(result, dict):
                if 'error' in result:
                    groom = f"Error: {result['error']}"
                elif 'enhanced_output' in result:
                    # Return the enhanced markdown + JSON output
                    groom = result['enhanced_output']
                elif 'markdown' in result:
                    # Return just the markdown if available
                    groom = result['markdown']
                else:
                    # Return structured data as JSON string
                    import json
                    groom = json.dumps(result, indent=2)
            else:
                groom = str(result)
        except Exception as e:
            groom = f"Error in enhanced analysis: {str(e)}"
            print(f"Enhanced analysis failed: {e}")
        print(f"Enhanced groom analysis generated, length={len(groom) if groom else 0}")
        print(f"Contains fallback message: {'temporarily unavailable' in groom if groom else False}")
        print(f"Response preview: {groom[:200] if groom else 'None'}...")
        
        return jsonify({
            'success': True,
            'data': {
                'groom': groom,
                'level': level,
                'ticket_number': ticket_number if ticket_number else None
            }
        })
        
    except Exception as e:
        print(f"ERROR in groomroom API: {e}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({
            'success': False,
            'error': f'Error generating groom analysis: {str(e)}',
            'error_type': type(e).__name__
        }), 500
    finally:
        print("=== GROOMROOM API CALL END ===")

@app.route('/api/groomroom/concise', methods=['POST'])
def generate_concise_groom():
    """Generate concise groom analysis from ticket content"""
    print("=== CONCISE GROOMROOM API CALL START ===")
    
    if not groomroom:
        print("ERROR: GroomRoom service not available")
        return jsonify({
            'success': False,
            'error': 'GroomRoom service not available'
        }), 503
    
    try:
        data = request.get_json()
        ticket_content = data.get('ticket_content', '')
        ticket_number = data.get('ticket_number', '')
        
        print(f"Request data: ticket_content length={len(ticket_content)}, ticket_number={ticket_number}")
        
        if not ticket_content and not ticket_number:
            print("ERROR: No ticket content or number provided")
            return jsonify({
                'success': False,
                'error': 'Either ticket_content or ticket_number must be provided'
            }), 400
        
        # Get ticket content from Jira if ticket number provided
        if ticket_number and not ticket_content:
            print(f"Fetching ticket {ticket_number} from Jira...")
            if not jira_integration or not jira_integration.is_available():
                print("ERROR: Jira integration not available")
                return jsonify({
                    'success': False,
                    'error': 'Jira integration not available'
                }), 503
            
            ticket_info = jira_integration.get_ticket_info(ticket_number)
            if ticket_info:
                ticket_content = jira_integration.format_ticket_for_analysis(ticket_info)
                print(f"Successfully fetched ticket content, length={len(ticket_content)}")
            else:
                print(f"ERROR: Could not fetch ticket {ticket_number}")
                return jsonify({
                    'success': False,
                    'error': f'Could not fetch ticket {ticket_number}'
                }), 404
        
        # Check if groomroom client is available
        print(f"GroomRoom client available: {groomroom.client is not None}")
        if not groomroom.client:
            print("ERROR: Azure OpenAI client not configured")
            return jsonify({
                'success': False,
                'error': 'Azure OpenAI client not configured. Please check environment variables.',
                'details': {
                    'endpoint_set': bool(os.getenv('AZURE_OPENAI_ENDPOINT')),
                    'api_key_set': bool(os.getenv('AZURE_OPENAI_API_KEY')),
                    'deployment_set': bool(os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'))
                }
            }), 503
        
        # Generate concise groom analysis
        print(f"Calling groomroom.generate_concise_groom_analysis")
        
        # Add request ID for debugging
        import time
        request_id = int(time.time())
        print(f"Request ID: {request_id}")
        print(f"Ticket content preview: {ticket_content[:200]}...")
        
        # Use enhanced analyze_ticket method with summary mode for concise output
        try:
            result = groomroom.analyze_ticket(ticket_content, mode="summary")
            if isinstance(result, dict) and 'enhanced_output' in result:
                groom = result['enhanced_output']
            elif isinstance(result, dict) and 'markdown' in result:
                groom = result['markdown']
            else:
                groom = str(result)
        except Exception as e:
            groom = f"Error in concise analysis: {str(e)}"
        print(f"Concise groom analysis generated, length={len(groom) if groom else 0}")
        print(f"Response preview: {groom[:200] if groom else 'None'}...")
        
        return jsonify({
            'success': True,
            'data': {
                'groom': groom,
                'ticket_number': ticket_number if ticket_number else None
            }
        })
        
    except Exception as e:
        print(f"ERROR in concise groomroom API: {e}")
        print(f"Error type: {type(e).__name__}")
        return jsonify({
            'success': False,
            'error': f'Error generating concise groom analysis: {str(e)}',
            'error_type': type(e).__name__
        }), 500
    finally:
        print("=== CONCISE GROOMROOM API CALL END ===")

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
        elif content_type == 'groomroom':
            teams_message = f"""
🧹 **Groom Room Analysis** {f'for {ticket_number}' if ticket_number else ''}

{content[:500]}{'...' if len(content) > 500 else ''}

*Generated by Groom Room Web App*
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

@app.route('/api/jira/dashboard/cards', methods=['GET'])
def get_jira_dashboard_cards():
    """Get Jira dashboard cards - proxy endpoint to avoid CORS"""
    if not jira_integration:
        return jsonify({
            'success': False,
            'error': 'Jira integration not available'
        }), 503
    
    try:
        # Get query parameters
        team_filter = request.args.get('team', 'all')
        status_filter = request.args.get('status', 'all')
        
        # Use the existing Jira integration to fetch cards
        cards = jira_integration.get_dashboard_cards(team_filter=team_filter, status_filter=status_filter)
        
        return jsonify({
            'success': True,
            'data': cards
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jira/dashboard/teams', methods=['GET'])
def get_jira_teams():
    """Get available Jira teams"""
    try:
        teams = jira_integration.get_available_teams()
        return jsonify({
            'success': True,
            'data': teams
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jira/dashboard/statuses', methods=['GET'])
def get_jira_statuses():
    """Get available Jira statuses"""
    try:
        statuses = jira_integration.get_available_statuses()
        return jsonify({
            'success': True,
            'data': statuses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 
