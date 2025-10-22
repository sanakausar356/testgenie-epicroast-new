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
        try:
            result = groomroom.analyze_ticket(content, mode=level)
        except Exception as e:
            # If Jira integration fails, provide helpful error message
            if ticket_number and "Could not fetch ticket" in str(e):
                return jsonify({
                    'success': False,
                    'error': f'Jira integration not configured. Please paste the ticket content manually or configure Jira credentials in Railway environment variables.',
                    'suggestion': 'Add JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN to Railway environment variables'
                }), 400
            else:
                raise e
        
        # Check if result is already formatted (has mode and display_format keys)
        if 'mode' in result and 'display_format' in result:
            # Result is already formatted, extract the formatted text
            formatted_output = _extract_formatted_text(result, level)
        else:
            # Result is raw, format it
            if level == 'insight':
                formatted_output = _format_insight_for_display(result)
            elif level == 'actionable':
                formatted_output = _format_actionable_for_display(result)
            elif level == 'summary':
                formatted_output = _format_summary_for_display(result)
            else:
                formatted_output = str(result)
        
        analysis = {
            'groom': formatted_output,
            'level': level,
            'ticket_number': ticket_number,
            'sprint_readiness': result.get('SprintReadiness', result.get('readiness_score', 0)),
            'type': result.get('Type', result.get('ticket_key', 'Unknown')),
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