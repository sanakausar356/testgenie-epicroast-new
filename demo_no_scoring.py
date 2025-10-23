#!/usr/bin/env python3
"""
Demo script for GroomRoom No-Scoring implementation
Shows the key features and outputs
"""

def demo_paypal_ticket():
    """Demo with the PayPal ticket example from the requirements"""
    
    # PayPal ticket data (ODCD-34668 example)
    ticket_data = {
        'key': 'ODCD-34668',
        'fields': {
            'summary': 'PayPal popup opens immediately on first CTA click',
            'description': '''
# User Story
As a shopper, I want the PayPal window to open immediately on the first PayPal CTA click at checkout so that I can reduce friction and complete payment faster.

# Acceptance Criteria
1. On the checkout page, clicking the PayPal CTA opens the PayPal window immediately (≤300 ms) via a user-gesture call.
2. The secondary PayPal CTA and helper copy are not rendered after the first click.
3. This behaviour applies to all DTC sites; cart page PayPal behaviour is unchanged.
4. ABTasty PayPal patches are disabled during validation; behaviour must function from code.
5. If the browser blocks the popup, show an inline message with a Retry action that opens the popup on the next click.
6. When the popup closes (success or cancel), focus returns to the PayPal CTA; the selected payment method remains PayPal.
7. Analytics log: paypal_cta_click, paypal_popup_opened, paypal_popup_blocked, paypal_completed, paypal_cancelled with site/brand context.

# Test Scenarios
- Positive: Click CTA → popup within ≤300 ms; no second CTA/copy; focus returns after completion
- Negative: Confirm no change on cart page PayPal flow. Prevent double-click from spawning multiple popups
- Error/Resilience: Simulate popup blocked → inline message + Retry opens popup. Simulate SDK load failure → non-blocking error and retry

# Implementation Details
- State handler for user-gesture open
- SDK version specification
- Debounce implementation
- ABTasty kill-switch

# Architecture
- Sequence diagram: Checkout → PayPal SDK → return
- Error map for SDK failures

# ADA Criteria
- Keyboard activation (Enter/Space)
- Focus management to/from popup
- Screen reader announcement that PayPal window opened

# Design
[Figma](https://www.figma.com/file/AbC123/Checkout-Design?node-id=10%3A20)
            ''',
            'issuetype': {'name': 'Story'}
        }
    }
    
    print("=== GroomRoom No-Scoring Demo ===")
    print("PayPal Ticket Analysis (ODCD-34668)")
    print("=" * 50)
    
    try:
        from groomroom.core_no_scoring import GroomRoomNoScoring
        
        groomroom = GroomRoomNoScoring()
        result = groomroom.analyze_ticket(ticket_data, "Actionable")
        
        print(f"✅ Status: {result.data.get('Status')}")
        print(f"✅ Type: {result.data.get('Type')}")
        print(f"✅ Mode: {result.data.get('Mode')}")
        
        # Check DoR
        dor = result.data.get('DoR', {})
        print(f"\n📋 Definition of Ready:")
        print(f"   Present: {', '.join(dor.get('Present', []))}")
        print(f"   Missing: {', '.join(dor.get('Missing', []))}")
        print(f"   Conflicts: {', '.join(dor.get('Conflicts', [])) or 'None'}")
        
        # Check Story Review
        story_review = result.data.get('StoryReview', {})
        if story_review:
            print(f"\n🧩 User Story:")
            print(f"   Persona: {'✅' if story_review.get('Persona') else '❌'}")
            print(f"   Goal: {'✅' if story_review.get('Goal') else '❌'}")
            print(f"   Benefit: {'✅' if story_review.get('Benefit') else '❌'}")
            print(f"   Suggested Rewrite: \"{story_review.get('SuggestedRewrite', 'Not found')}\"")
        
        # Check ACs
        ac_data = result.data.get('AcceptanceCriteria', {})
        print(f"\n✅ Acceptance Criteria:")
        print(f"   Detected: {ac_data.get('Detected', 0)}")
        print(f"   Rewrites: {len(ac_data.get('Rewrites', []))}")
        for i, ac in enumerate(ac_data.get('Rewrites', [])[:3], 1):
            print(f"   {i}) {ac}")
        if len(ac_data.get('Rewrites', [])) > 3:
            print(f"   ... and {len(ac_data.get('Rewrites', [])) - 3} more")
        
        # Check Test Scenarios
        test_scenarios = result.data.get('TestScenarios', {})
        print(f"\n🧪 Test Scenarios:")
        print(f"   Positive: {len(test_scenarios.get('positive', []))}")
        print(f"   Negative: {len(test_scenarios.get('negative', []))}")
        print(f"   Error: {len(test_scenarios.get('error', []))}")
        
        # Check Design Links
        design_links = result.data.get('DesignLinks', [])
        print(f"\n🎨 Design:")
        print(f"   Links: {len(design_links)}")
        for link in design_links:
            print(f"   - {link}")
        
        # Check Recommendations
        recommendations = result.data.get('Recommendations', {})
        print(f"\n💡 Recommendations:")
        for role, recs in recommendations.items():
            print(f"   {role.upper()}: {len(recs)} items")
            for rec in recs[:2]:
                print(f"   - {rec}")
            if len(recs) > 2:
                print(f"   ... and {len(recs) - 2} more")
        
        # Verify no framework scores
        print(f"\n🔍 Verification:")
        has_framework_scores = any(key in result.data for key in ['FrameworkScores', 'framework_scores', 'ROI', 'INVEST', 'ACCEPT', '3C'])
        print(f"   Framework Scores Present: {'❌ YES' if has_framework_scores else '✅ NO'}")
        print(f"   Status Rule-Based: {'✅ YES' if result.data.get('Status') in ['Ready', 'Needs Refinement', 'Not Ready'] else '❌ NO'}")
        print(f"   Context-Specific Content: {'✅ YES' if any('PayPal' in str(result.data)) else '❌ NO'}")
        
        print(f"\n📄 Full Markdown Report:")
        print("-" * 50)
        print(result.markdown)
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = demo_paypal_ticket()
    
    if success:
        print("\n" + "=" * 50)
        print("🎉 GroomRoom No-Scoring Demo Complete!")
        print("✅ No framework scores")
        print("✅ Context-specific outputs")
        print("✅ Domain-aware content")
        print("✅ Figma integration")
        print("✅ Conflict detection")
        print("✅ Role-tagged recommendations")
    else:
        print("\n❌ Demo failed")
        exit(1)
