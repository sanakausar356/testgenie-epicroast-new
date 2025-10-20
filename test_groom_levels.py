"""
Test script for the new 3 Groom Levels
"""

import json
from groomroom.core import GroomRoom

def test_groom_levels():
    """Test all 3 groom levels with sample ticket"""
    print("🧩 Testing New Groom Levels")
    print("=" * 60)
    
    groomroom = GroomRoom()
    
    # Sample ticket for testing
    test_ticket = """
    As a customer, I want to apply discount codes at checkout so that I can save money on my purchases.
    
    Acceptance Criteria:
    - User can enter discount code
    - System validates the code
    - Discount is applied to total
    
    Test Scenarios:
    - Valid code applies discount
    - Invalid code shows error
    """
    
    print(f"📋 Test Ticket: {test_ticket.strip()[:100]}...")
    print()
    
    # Test each groom level
    levels = ['insight', 'actionable', 'summary']
    
    for level in levels:
        print(f"\n{'='*20} {level.upper()} MODE {'='*20}")
        
        result = groomroom.analyze_ticket(test_ticket, mode=level)
        
        # Display formatted output based on mode
        if level == 'insight':
            display_insight_output(result)
        elif level == 'actionable':
            display_actionable_output(result)
        elif level == 'summary':
            display_summary_output(result)
        
        print()

def display_insight_output(result):
    """Display Insight mode output in readable summary format"""
    print(f"🔍 Insight Analysis (Story: {result.get('ticket_key', 'Unknown')})")
    print()
    
    readiness = result.get('readiness_percentage', 0)
    status = result.get('readiness_status', 'Unknown')
    print(f"Readiness: {readiness}% ({status})")
    
    weak_areas = result.get('weak_areas', [])
    if weak_areas:
        print(f"Weak Areas: {', '.join(weak_areas)}")
    
    # Story clarity
    story_clarity = result.get('story_clarity', {})
    assessment = story_clarity.get('assessment', 'Unknown')
    persona_detected = story_clarity.get('persona_goal_detected', False)
    print(f"\nStory Clarity: {assessment} — Persona and Goal detected {'✅' if persona_detected else '❌'}")
    
    suggested_rewrite = story_clarity.get('suggested_rewrite')
    if suggested_rewrite:
        print(f"Suggested rewrite: \"{suggested_rewrite}\"")
    
    # AC Quality
    ac_info = result.get('acceptance_criteria', {})
    detected = ac_info.get('detected_count', 0)
    weak = ac_info.get('weak_count', 0)
    print(f"\nAC Quality: {detected} found ({weak} vague)")
    if weak > 0:
        print("→ Add AC for edge case handling")
    
    # Test Scenarios
    test_scenarios = result.get('test_scenarios', [])
    if test_scenarios:
        print(f"\nSuggested Test Scenarios:")
        for scenario in test_scenarios[:3]:
            print(f"• {scenario}")
    
    # Framework Summary
    framework = result.get('framework_summary', {})
    print(f"\nFramework Summary:")
    print(f"ROI: {framework.get('roi', 0)} | INVEST: {framework.get('invest', 0)} | ACCEPT: {framework.get('accept', 0)} | 3C: {framework.get('3c', 0)}")

def display_actionable_output(result):
    """Display Actionable mode output in structured sections"""
    print(f"⚡ Actionable Groom Report ({result.get('ticket_key', 'Unknown')})")
    readiness = result.get('readiness_score', 0)
    status = result.get('readiness_status', 'Unknown')
    print(f"Readiness: {readiness}% | Status: {status}")
    print()
    
    sections = result.get('sections', {})
    
    # User Story section
    user_story = sections.get('user_story', {})
    print(f"{user_story.get('title', '🧩 User Story')}")
    persona_found = user_story.get('persona_goal_found', False)
    benefit_clarity = user_story.get('benefit_clarity', 'Unknown')
    print(f"- Persona/Goal found {'✅' if persona_found else '❌'}")
    print(f"- Benefit {benefit_clarity.lower()}")
    
    suggested_rewrite = user_story.get('suggested_rewrite')
    if suggested_rewrite:
        print(f"- Suggested rewrite provided")
    
    missing_business = user_story.get('missing_business_metric', False)
    if missing_business:
        print(f"- Missing business metric reference (ROI impact)")
    
    # Acceptance Criteria section
    ac_section = sections.get('acceptance_criteria', {})
    print(f"\n{ac_section.get('title', '✅ Acceptance Criteria')}")
    detected = ac_section.get('detected_count', 0)
    need_rewriting = ac_section.get('need_rewriting', 0)
    print(f"- {detected} detected | {need_rewriting} need rewriting for measurability")
    
    suggested_rewrites = ac_section.get('suggested_rewrites', [])
    if suggested_rewrites:
        print("Suggested rewrite examples:")
        for i, rewrite in enumerate(suggested_rewrites[:2], 1):
            print(f"{i}. \"{rewrite}\"")
    
    # QA Scenarios section
    qa_section = sections.get('qa_scenarios', {})
    print(f"\n{qa_section.get('title', '🧪 QA Scenarios')}")
    suggested_scenarios = qa_section.get('suggested_scenarios', [])
    if suggested_scenarios:
        for scenario in suggested_scenarios[:2]:
            print(f"- {scenario}")
    
    missing_negative = qa_section.get('missing_negative_flow', False)
    if missing_negative:
        print("- Add test for negative flow scenarios")
    
    # Technical/ADA section
    tech_section = sections.get('technical_ada', {})
    print(f"\n{tech_section.get('title', '🧱 Technical / ADA')}")
    missing_arch = tech_section.get('missing_architectural_solution', False)
    missing_ada = tech_section.get('missing_ada_criteria', False)
    
    if missing_arch:
        print("- Missing Architectural Solution link")
    if missing_ada:
        print("- No ADA criteria for contrast or keyboard focus")

def display_summary_output(result):
    """Display Summary mode output in compact card format"""
    ticket_key = result.get('ticket_key', 'Unknown')
    readiness = result.get('readiness_percentage', 0)
    status = result.get('readiness_status', 'Unknown')
    
    print(f"📋 Summary — {ticket_key} | Sprint Readiness: {readiness}%")
    print(f"Status: {status}")
    print()
    
    # Top Gaps
    top_gaps = result.get('top_gaps', [])
    if top_gaps:
        print("Top Gaps:")
        for i, gap in enumerate(top_gaps, 1):
            print(f"{i}. {gap}")
    
    # Recommended Actions
    recommended_actions = result.get('recommended_actions', [])
    if recommended_actions:
        print("\nRecommended Actions:")
        for action in recommended_actions:
            print(f"→ {action}")

def main():
    """Run groom levels test"""
    try:
        test_groom_levels()
        print("\n" + "="*60)
        print("✅ All 3 Groom Levels tested successfully!")
        print("\n🎯 Groom Levels Summary:")
        print("• Insight: Balanced analysis for refinement meetings")
        print("• Actionable: Deep prescriptive guidance for QA handoff")
        print("• Summary: Quick snapshot for leads and dashboards")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
