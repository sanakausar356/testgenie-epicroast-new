#!/usr/bin/env python3
"""
TestGenie & EpicRoast with GroomRoom - Flask Backend API
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
import os
import sys 

 # ⬅️ add this

# ensure project root on sys.path so we can import groomroom/* and jira_integration.py
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from jira_integration import JiraIntegration  # ⬅️ add this


# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
jira = JiraIntegration() 

def _format_insight_for_display(result):
    """Format insight mode output for display"""
    readiness = result.get('SprintReadiness', 0)
    status = "Ready for Dev" if readiness >= 90 else "Needs minor refinement" if readiness >= 70 else "Not Ready"
    
    missing_fields = result.get('DefinitionOfReady', {}).get('MissingFields', [])
    top_gaps = missing_fields[:3]
    
    story_analysis = result.get('StoryAnalysis', {})
    story_quality = story_analysis.get('story_quality_score', 0)
    story_clarity = "Good" if story_quality >= 70 else "Needs improvement"
    
    framework_scores = result.get('FrameworkScores', {})
    
    output = f"""🔍 Insight Analysis (Story: {result.get('TicketKey', 'Unknown')})

Readiness: {readiness}% ({status})
Weak Areas: {', '.join(top_gaps) if top_gaps else 'None detected'}

Story Clarity: {story_clarity} — Persona and Goal detected {'✅' if story_analysis.get('has_clear_structure', False) else '❌'}"""
    
    suggested_rewrite = result.get('StoryRewrite')
    if suggested_rewrite:
        output += f"\nSuggested rewrite: \"{suggested_rewrite}\""
    
    ac_audit = result.get('AcceptanceCriteriaAudit', {})
    detected = ac_audit.get('Detected', 0)
    weak = ac_audit.get('Weak', 0)
    output += f"\n\nAC Quality: {detected} found ({weak} vague)"
    if weak > 0:
        output += "\n→ Add AC for edge case handling"
    
    test_scenarios = result.get('SuggestedTestScenarios', [])
    if test_scenarios:
        output += f"\n\nSuggested Test Scenarios:"
        for scenario in test_scenarios[:3]:
            output += f"\n• {scenario}"
    
    output += f"\n\nFramework Summary:"
    output += f"\nROI: {framework_scores.get('ROI', 0)} | INVEST: {framework_scores.get('INVEST', 0)} | ACCEPT: {framework_scores.get('ACCEPT', 0)} | 3C: {framework_scores.get('3C', 0)}"
    
    return output

def _format_actionable_for_display(result):
    """Format actionable mode output for display"""
    readiness = result.get('SprintReadiness', 0)
    status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
    status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
    
    output = f"""⚡ Actionable Groom Report ({result.get('TicketKey', 'Unknown')})
Readiness: {readiness}% | Status: {status_emoji} {status_text}

🧩 User Story"""
    
    story_analysis = result.get('StoryAnalysis', {})
    persona_found = story_analysis.get('has_clear_structure', False)
    benefit_clarity = "Clear" if story_analysis.get('story_quality_score', 0) >= 70 else "Unclear"
    
    output += f"\n- Persona/Goal found {'✅' if persona_found else '❌'}"
    output += f"\n- Benefit {benefit_clarity.lower()}"
    
    suggested_rewrite = result.get('StoryRewrite')
    if suggested_rewrite:
        output += f"\n- Suggested rewrite provided"
    
    output += f"\n\n✅ Acceptance Criteria"
    ac_audit = result.get('AcceptanceCriteriaAudit', {})
    detected = ac_audit.get('Detected', 0)
    need_rewriting = ac_audit.get('Weak', 0)
    output += f"\n- {detected} detected | {need_rewriting} need rewriting for measurability"
    
    suggested_rewrites = ac_audit.get('SuggestedRewrite', [])
    if suggested_rewrites:
        output += "\nSuggested rewrite examples:"
        for i, rewrite in enumerate(suggested_rewrites[:2], 1):
            output += f"\n{i}. \"{rewrite}\""
    
    output += f"\n\n🧪 QA Scenarios"
    test_scenarios = result.get('SuggestedTestScenarios', [])
    if test_scenarios:
        for scenario in test_scenarios[:2]:
            output += f"\n- {scenario}"
    
    output += f"\n\n🧱 Technical / ADA"
    missing_fields = result.get('DefinitionOfReady', {}).get('MissingFields', [])
    if "Architectural Solution" in missing_fields:
        output += "\n- Missing Architectural Solution link"
    if "ADA Criteria" in missing_fields:
        output += "\n- No ADA criteria for contrast or keyboard focus"
    
    return output

def _format_summary_for_display(result):
    """Format summary mode output for display"""
    readiness = result.get('SprintReadiness', 0)
    status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
    status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
    
    ticket_key = result.get('TicketKey', 'Unknown')
    missing_fields = result.get('DefinitionOfReady', {}).get('MissingFields', [])
    top_gaps = missing_fields[:3]
    recommendations = result.get('Recommendations', [])[:3]
    
    output = f"""📋 Summary — {ticket_key} | Sprint Readiness: {readiness}%
Status: {status_emoji} {status_text}"""
    
    if top_gaps:
        output += "\n\nTop Gaps:"
        for i, gap in enumerate(top_gaps, 1):
            output += f"\n{i}. {gap}"
    
    if recommendations:
        output += "\n\nRecommended Actions:"
        for action in recommendations:
            output += f"\n→ {action}"
    
    return output

def _extract_formatted_text(result, level):
    """Extract formatted text from already-formatted GroomRoom result"""
    if level == 'actionable':
        return _format_actionable_from_structured(result)
    elif level == 'insight':
        return _format_insight_from_structured(result)
    elif level == 'summary':
        return _format_summary_from_structured(result)
    else:
        return str(result)

def _format_actionable_from_structured(result):
    """Format actionable output from structured result"""
    readiness = result.get('readiness_score', 0)
    status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
    status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
    
    output = f"""⚡ Actionable Groom Report ({result.get('ticket_key', 'Unknown')})
Readiness: {readiness}% | Status: {status_emoji} {status_text}

🧩 User Story"""
    
    sections = result.get('sections', {})
    user_story = sections.get('user_story', {})
    persona_found = user_story.get('persona_goal_found', False)
    benefit_clarity = user_story.get('benefit_clarity', 'Unclear')
    
    output += f"\n- Persona/Goal found {'✅' if persona_found else '❌'}"
    output += f"\n- Benefit {benefit_clarity.lower()}"
    
    if user_story.get('suggested_rewrite'):
        output += f"\n- Suggested rewrite provided"
    
    output += f"\n\n✅ Acceptance Criteria"
    ac_section = sections.get('acceptance_criteria', {})
    detected = ac_section.get('detected_count', 0)
    need_rewriting = ac_section.get('need_rewriting', 0)
    output += f"\n- {detected} detected | {need_rewriting} need rewriting for measurability"
    
    suggested_rewrites = ac_section.get('suggested_rewrites', [])
    if suggested_rewrites:
        output += "\nSuggested rewrite examples:"
        for i, rewrite in enumerate(suggested_rewrites[:2], 1):
            output += f"\n{i}. \"{rewrite}\""
    
    output += f"\n\n🧪 QA Scenarios"
    qa_section = sections.get('qa_scenarios', {})
    test_scenarios = qa_section.get('suggested_scenarios', [])
    if test_scenarios:
        for scenario in test_scenarios[:2]:
            output += f"\n- {scenario}"
    
    output += f"\n\n🧱 Technical / ADA"
    tech_section = sections.get('technical_ada', {})
    if tech_section.get('missing_architectural_solution'):
        output += "\n- Missing Architectural Solution link"
    if tech_section.get('missing_ada_criteria'):
        output += "\n- No ADA criteria for contrast or keyboard focus"
    
    return output

def _format_insight_from_structured(result):
    """Format insight output from structured result"""
    # For now, return a simple insight format
    readiness = result.get('readiness_score', 0)
    status = "Ready for Dev" if readiness >= 90 else "Needs minor refinement" if readiness >= 70 else "Not Ready"
    
    return f"""🔍 Insight Analysis ({result.get('ticket_key', 'Unknown')})
Readiness: {readiness}% ({status})
Status: {'✅' if readiness >= 90 else '⚠️' if readiness >= 70 else '❌'} {status}"""

def _format_summary_from_structured(result):
    """Format summary output from structured result"""
    readiness = result.get('readiness_score', 0)
    status_emoji = "✅" if readiness >= 90 else "⚠️" if readiness >= 70 else "❌"
    status_text = "Ready for Dev" if readiness >= 90 else "Needs Refinement" if readiness >= 70 else "Not Ready"
    
    return f"""📋 Summary — {result.get('ticket_key', 'Unknown')} | Sprint Readiness: {readiness}%
Status: {status_emoji} {status_text}"""

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
@app.route('/api/groomroom/generate', methods=['POST'])  # Support old endpoint for compatibility
def generate_groom():
    """Generate GroomRoom analysis (rich Jira context → markdown)."""
    try:
        data = request.get_json(force=True) or {}
        ticket_number = (data.get('ticket_number') or '').strip()
        ticket_content = (data.get('ticket_content') or '').strip()
        level = (data.get('level') or 'actionable').strip().lower()
        figma_link = (data.get('figma_link') or '').strip() or None

        # normalize level
        if level not in ('insight', 'actionable', 'summary'):
            level = 'actionable'

        # Fetch from Jira if ticket_number provided, otherwise use pasted content
        ticket_data = None
        
        if ticket_number:
            # Fetch directly from Jira using fetch_ticket
            if hasattr(jira, "fetch_ticket"):
                print(f"Fetching ticket {ticket_number}...")
                jira_ticket = jira.fetch_ticket(ticket_number)
                if not jira_ticket:
                    return jsonify({"success": False, "error": f"Could not fetch ticket {ticket_number}"}), 404, {'Content-Type': 'application/json; charset=utf-8'}
                # Pass real Jira ticket data to core_no_scoring
                ticket_data = jira_ticket
                print(f"Ticket info created successfully")
            else:
                # Fallback: build corpus and create fake ticket_data
                if hasattr(jira, "build_rich_context"):
                    rich = jira.build_rich_context(ticket_number)
                    if not rich or not rich.get("issue"):
                        return jsonify({"success": False, "error": f"Could not fetch ticket {ticket_number}"}), 404, {'Content-Type': 'application/json; charset=utf-8'}
                    content = rich["corpus"]
                    if ticket_content:
                        content = f"{content}\n\nUser Paste:\n{ticket_content}"
                    ticket_data = {
                        'key': ticket_number,
                        'fields': {
                            'summary': f'Ticket {ticket_number}',
                            'description': content,
                            'issuetype': {'name': 'Story'}
                        }
                    }
                else:
                    return jsonify({"success": False, "error": "Jira integration not available"}), 500, {'Content-Type': 'application/json; charset=utf-8'}
        
        elif figma_link:
            # Fetch from Figma using figma_link
            try:
                from figma_integration import extract_figma_as_ticket
                print(f"📋 Extracting Figma design from: {figma_link}")
                ticket_data = extract_figma_as_ticket(figma_link)
                print(f"✅ Figma extraction completed: {ticket_data['key']}")
            except Exception as figma_error:
                return jsonify({
                    "success": False, 
                    "error": f"Figma extraction failed: {str(figma_error)}"
                }), 400, {'Content-Type': 'application/json; charset=utf-8'}
        
        else:
            # Use pasted content
            if not ticket_content:
                return jsonify({"success": False, "error": "Provide 'ticket_content', 'ticket_number', or 'figma_link'"}), 400, {'Content-Type': 'application/json; charset=utf-8'}
            ticket_data = {
                'key': 'PASTED-CONTENT',
                'fields': {
                    'summary': 'Pasted Content Analysis',
                    'description': ticket_content,
                    'issuetype': {'name': 'Story'}
                }
            }

        groom = None

        # 1) Try No-Scoring implementation
        try:
            from groomroom.core_no_scoring import GroomRoomNoScoring
            gr = GroomRoomNoScoring()

            result = gr.analyze_ticket(ticket_data, level.title())

            # prefer attribute .markdown, else dict key, else stringify
            groom = getattr(result, "markdown", None)
            if groom is None and isinstance(result, dict):
                groom = result.get("markdown")
            if groom is None:
                groom = str(result)

            print(f"GroomRoom No-Scoring analysis completed for level: {level}")

        except Exception as _no_scoring_err:
            # 2) Fallback to original GroomRoom
            try:
                from groomroom.core import GroomRoom
                gr = GroomRoom()

                result = gr.analyze_ticket(content, mode=level, figma_link=figma_link)

                if isinstance(result, dict):
                    if 'error' in result:
                        groom = f"Error: {result['error']}"
                    elif 'markdown' in result:                 # new patched core.py
                        groom = result['markdown']
                    elif 'enhanced_output' in result:          # legacy core output
                        groom = result['enhanced_output']
                    else:
                        import json
                        groom = json.dumps(result, indent=2)
                else:
                    groom = str(result)

                print(f"GroomRoom fallback analysis completed for level: {level}")
            except Exception as e2:
                print("Fallback failed:", e2)
                # surface the original no-scoring error if both fail
                raise _no_scoring_err

        print(f"Groom analysis generated, length={len(groom) if groom else 0}")
        
        # Extract structured_data from result if available
        structured_data = None
        if hasattr(result, 'data'):
            structured_data = result.data
        elif isinstance(result, dict) and 'data' in result:
            structured_data = result['data']
        
        return jsonify({
            'success': True,
            'data': {
                'groom': groom,
                'level': level,
                'ticket_number': ticket_number or None,
                'figma_link': figma_link
            },
            'structured_data': structured_data,
            'readiness_percentage': structured_data.get('SprintReadiness', 0) if structured_data else 0,
            'status': structured_data.get('Status', '') if structured_data else ''
        }), 200, {'Content-Type': 'application/json; charset=utf-8'}

    except Exception as e:
        print(f"Error in generate_groom: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500, {'Content-Type': 'application/json; charset=utf-8'}

@app.route('/api/groomroom/vnext/analyze', methods=['POST'])
def analyze_ticket_vnext():
    """Analyze ticket using GroomRoom vNext"""
    try:
        data = request.get_json()
        ticket_data = data.get('ticket_data', {})
        mode = data.get('mode', 'Actionable')
        
        # Import GroomRoom vNext
        try:
            from groomroom.core_vnext import GroomRoomVNext
            groomroom = GroomRoomVNext()
            result = groomroom.analyze_ticket(ticket_data, mode)
            
            return jsonify({
                'success': True,
                'data': {
                    'markdown': result.markdown,
                    'json_data': result.data
                }
            })
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'GroomRoom vNext not available'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/groomroom/vnext/batch', methods=['POST'])
def analyze_batch_vnext():
    """Analyze multiple tickets using GroomRoom vNext"""
    try:
        data = request.get_json()
        tickets = data.get('tickets', [])
        mode = data.get('mode', 'Summary')
        
        # Import GroomRoom vNext
        try:
            from groomroom.core_vnext import GroomRoomVNext
            groomroom = GroomRoomVNext()
            
            results = []
            for ticket in tickets:
                result = groomroom.analyze_ticket(ticket, mode)
                results.append({
                    'ticket_key': result.data.get('TicketKey', 'Unknown'),
                    'readiness_score': result.data.get('Readiness', {}).get('Score', 0),
                    'status': result.data.get('Readiness', {}).get('Status', 'Not Ready'),
                    'design_links': result.data.get('DesignLinks', []),
                    'summary': result.markdown[:200] + '...' if len(result.markdown) > 200 else result.markdown
                })
            
            # Generate batch summary
            ready_count = sum(1 for r in results if r['status'] == 'Ready')
            needs_refinement = sum(1 for r in results if r['status'] == 'Needs Refinement')
            not_ready = sum(1 for r in results if r['status'] == 'Not Ready')
            avg_score = sum(r['readiness_score'] for r in results) // len(results) if results else 0
            
            return jsonify({
                'success': True,
                'data': {
                    'results': results,
                    'summary': {
                        'total_tickets': len(results),
                        'ready': ready_count,
                        'needs_refinement': needs_refinement,
                        'not_ready': not_ready,
                        'average_score': avg_score
                    }
                }
            })
        except ImportError:
            return jsonify({
                'success': False,
                'error': 'GroomRoom vNext not available'
            }), 500
        
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
@app.route('/api/epicroast/generate', methods=['POST'])
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
