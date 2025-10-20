"""
Test script for refactored GroomRoom Refinement Agent
"""

import json
from groomroom.core import GroomRoom

def test_user_story_analysis():
    """Test user story analysis"""
    print("\n" + "="*80)
    print("TEST 1: User Story Analysis")
    print("="*80)
    
    groomroom = GroomRoom()
    
    test_ticket = """
    As a customer, I want to see delivery dates on the product detail page,
    so that I can plan my purchases better.
    
    Acceptance Criteria:
    - Display estimated delivery date
    - Show message if delivery not available
    - Update date based on postal code
    
    Test Scenarios:
    - Verify delivery date appears correctly
    """
    
    result = groomroom.analyze_ticket(test_ticket, mode="actionable")
    
    print(f"\nTicket Key: {result.get('TicketKey')}")
    print(f"Type: {result.get('Type')}")
    print(f"Sprint Readiness: {result.get('SprintReadiness')}%")
    print(f"\nStory Rewrite: {result.get('StoryRewrite')}")
    print(f"\nAC Audit:")
    print(f"  - Detected: {result.get('AcceptanceCriteriaAudit', {}).get('Detected')}")
    print(f"  - Weak: {result.get('AcceptanceCriteriaAudit', {}).get('Weak')}")
    print(f"\nTest Scenarios: {len(result.get('SuggestedTestScenarios', []))}")
    print(f"\nRecommendations:")
    for rec in result.get('Recommendations', [])[:5]:
        print(f"  - {rec}")
    
    return result

def test_bug_analysis():
    """Test bug analysis"""
    print("\n" + "="*80)
    print("TEST 2: Bug Analysis")
    print("="*80)
    
    groomroom = GroomRoom()
    
    test_bug = """
    Login button not working on mobile devices
    
    Current Behavior:
    When users click the login button on mobile, nothing happens.
    
    Steps to Reproduce:
    1. Open app on mobile device
    2. Navigate to login page
    3. Enter credentials
    4. Click login button
    
    Expected Behavior:
    User should be logged in and redirected to dashboard.
    """
    
    result = groomroom.analyze_ticket(test_bug, mode="actionable")
    
    print(f"\nTicket Key: {result.get('TicketKey')}")
    print(f"Type: {result.get('Type')}")
    print(f"Sprint Readiness: {result.get('SprintReadiness')}%")
    
    if result.get('BugAudit'):
        bug_audit = result['BugAudit']
        print(f"\nBug Completeness: {bug_audit.get('completeness_score')}%")
        print(f"Is Complete: {bug_audit.get('is_complete')}")
        if bug_audit.get('suggestions'):
            print(f"\nSuggestions:")
            for sug in bug_audit['suggestions']:
                print(f"  - {sug}")
    
    return result

def test_framework_scoring():
    """Test framework scoring"""
    print("\n" + "="*80)
    print("TEST 3: Framework Scoring")
    print("="*80)
    
    groomroom = GroomRoom()
    
    test_ticket = """
    As a user, I want to reset my password so that I can access my account.
    
    This is a valuable feature that will help users regain access.
    The implementation will be small and focused on password reset flow.
    We need to verify the email verification process works correctly.
    
    Acceptance Criteria:
    - User can request password reset
    - Email is sent with reset link
    - Link expires after 24 hours
    - User can set new password
    """
    
    result = groomroom.analyze_ticket(test_ticket, mode="insight")
    
    print(f"\nFramework Scores:")
    for framework, score in result.get('FrameworkScores', {}).items():
        print(f"  {framework}: {score}/30" if framework != '3C' else f"  {framework}: {score}/10")
    
    if result.get('Insights'):
        insights = result['Insights']
        print(f"\nReadiness Breakdown:")
        for key, value in insights.get('ReadinessBreakdown', {}).items():
            print(f"  {key}: {value:.1f}")
    
    return result

def test_modes():
    """Test different analysis modes"""
    print("\n" + "="*80)
    print("TEST 4: Different Analysis Modes")
    print("="*80)
    
    groomroom = GroomRoom()
    
    test_ticket = "As a user, I want to view my order history."
    
    modes = ['strict', 'light', 'actionable', 'deepdive']
    
    for mode in modes:
        print(f"\n--- Mode: {mode} ---")
        result = groomroom.analyze_ticket(test_ticket, mode=mode)
        print(f"Keys in result: {list(result.keys())}")
        print(f"Sprint Readiness: {result.get('SprintReadiness')}%")
    
    return True

def test_batch_analysis():
    """Test batch analysis with summary"""
    print("\n" + "="*80)
    print("TEST 5: Batch Analysis with Summary")
    print("="*80)
    
    groomroom = GroomRoom()
    
    tickets = [
        "As a user, I want to see my profile",
        "As a user, I want to edit my settings",
        "Login button broken on mobile"
    ]
    
    results = []
    for ticket in tickets:
        result = groomroom.analyze_ticket(ticket, mode="light")
        results.append(result)
    
    summary = groomroom.summarize_output(results)
    
    print(f"\nSummary: {summary.get('Summary')}")
    print(f"Average Readiness: {summary.get('AverageReadiness'):.1f}%")
    print(f"\nTop Issues:")
    for issue in summary.get('TopIssues', []):
        print(f"  - {issue['field']}: {issue['count']} occurrences")
    
    return summary

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("GROOMROOM REFINEMENT AGENT - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    try:
        # Run tests
        test_user_story_analysis()
        test_bug_analysis()
        test_framework_scoring()
        test_modes()
        test_batch_analysis()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nGroomRoom refinement agent updated successfully — ready for testing on Jira input.")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

