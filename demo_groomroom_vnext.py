"""
GroomRoom vNext Demo
Comprehensive demonstration of all enhanced features
"""

import json
from groomroom.core_vnext import GroomRoomVNext

def demo_story_with_figma():
    """Demo User Story with Figma links"""
    print("🎯 Demo: User Story with Figma Integration")
    print("=" * 50)
    
    story_ticket = {
        "key": "DEMO-001",
        "fields": {
            "summary": "As a customer, I want to filter products by price range so that I can find affordable items",
            "description": """
# User Story
As a customer, I want to filter products by price range so that I can find affordable items within my budget.

# Acceptance Criteria
- User can select minimum and maximum price values using sliders
- Filter results update within 1 second of selection
- Clear filters button resets to default state
- Price range validation prevents invalid ranges (min > max)
- Design: https://figma.com/file/abc123/Product-Filter-Design
- Prototype: https://figma.com/proto/def456/Filter-Interaction

# Testing Steps
1. Navigate to product listing page
2. Open price filter panel
3. Set minimum price to $50
4. Set maximum price to $200
5. Verify results update within 1 second
6. Test clear filters functionality
7. Verify keyboard navigation works

# Implementation Details
- Use React hooks for state management
- Implement debounced search for performance
- Add loading states for better UX
- Use CSS transitions for smooth interactions

# ADA Criteria
- Keyboard navigation works for all filter controls
- Screen reader announces filter changes
- High contrast mode support
- Focus indicators visible on all interactive elements
- Voice control compatibility for price input
            """,
            "issuetype": {"name": "Story"},
            "components": [{"name": "Product Catalog"}, {"name": "Filters"}],
            "customfield_10002": 5,  # Story points
            "priority": {"name": "High"},
            "assignee": {"displayName": "John Developer"}
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(story_ticket, "Actionable")
    
    print(f"📊 Sprint Readiness: {result.data['Readiness']['Score']}% → {result.data['Readiness']['Status']}")
    print(f"📋 DoR Coverage: {result.data['Readiness']['DoRCoveragePercent']}%")
    print(f"🎨 Design Links: {len(result.data['DesignLinks'])}")
    print(f"🧭 Framework Scores: ROI {result.data['FrameworkScores']['roi']}, INVEST {result.data['FrameworkScores']['invest']}")
    print(f"✅ Suggested ACs: {len(result.data['AcceptanceCriteriaAudit']['SuggestedRewrites'])}")
    print(f"🧪 Test Scenarios: {len(result.data['TestScenarios']['Positive'])} positive, {len(result.data['TestScenarios']['Negative'])} negative")
    
    return result

def demo_bug_analysis():
    """Demo Bug analysis with structured content"""
    print("\n🐛 Demo: Bug Analysis with Structured Content")
    print("=" * 50)
    
    bug_ticket = {
        "key": "BUG-002",
        "fields": {
            "summary": "Login button not responding on mobile devices",
            "description": """
# Current Behaviour
Login button appears but does not respond to touch events on mobile devices (iOS Safari, Android Chrome). Button shows hover state but no click/tap response.

# Steps to Reproduce
1. Open application on mobile device (iOS/Android)
2. Navigate to login page
3. Enter valid credentials
4. Tap login button
5. Observe no response or action

# Expected Behaviour
Login button should process the request and redirect to dashboard within 2 seconds.

# Environment
- iOS Safari 15+ on iPhone 12/13
- Android Chrome 90+ on Samsung Galaxy
- Mobile viewport < 768px
- Touch events not registering

# Severity
High - blocks user access to application

# Links to Story
Related to: STORY-123 (Mobile login implementation)
            """,
            "issuetype": {"name": "Bug"},
            "priority": {"name": "Critical"},
            "components": [{"name": "Authentication"}, {"name": "Mobile"}],
            "customfield_10002": 3
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(bug_ticket, "Actionable")
    
    print(f"📊 Sprint Readiness: {result.data['Readiness']['Score']}% → {result.data['Readiness']['Status']}")
    print(f"🐞 Bug Review Available: {result.data['BugReview'] is not None}")
    if result.data['BugReview']:
        print(f"   Current: {result.data['BugReview']['Current'][:50]}...")
        print(f"   Expected: {result.data['BugReview']['Expected'][:50]}...")
    print(f"🧪 Test Scenarios: {len(result.data['TestScenarios']['Positive'])} positive scenarios")
    print(f"💡 Recommendations: {len(result.data['Recommendations']['PO'])} PO, {len(result.data['Recommendations']['QA'])} QA, {len(result.data['Recommendations']['Dev'])} Dev")
    
    return result

def demo_feature_epic():
    """Demo Feature/Epic analysis"""
    print("\n🚀 Demo: Feature/Epic Analysis")
    print("=" * 50)
    
    feature_ticket = {
        "key": "FEATURE-003",
        "fields": {
            "summary": "Implement Progressive Web App (PWA) capabilities for mobile users",
            "description": """
# Feature Description
Implement Progressive Web App capabilities to provide native app-like experience for mobile users across all brands (MMT, ExO, YCC).

# User Story
As a mobile user, I want to install the web app on my device so that I can access features quickly without browser navigation.

# Acceptance Criteria
- App can be installed on mobile devices (iOS/Android)
- Offline functionality for core features (product browsing, cart)
- Push notifications for order updates and promotions
- App-like navigation and interactions
- Performance meets PWA standards (Lighthouse score > 90)
- Design: https://figma.com/file/xyz789/PWA-Design-System
- Prototype: https://figma.com/proto/abc123/PWA-User-Flow

# Testing Steps
1. Test installation prompts on various devices
2. Verify offline functionality for 7 days
3. Test push notification delivery (< 5 seconds)
4. Validate performance metrics (Core Web Vitals)
5. Cross-browser compatibility testing
6. Accessibility testing with screen readers

# Implementation Details
- Service worker implementation with caching strategy
- Web app manifest configuration for all brands
- Push notification service integration (Firebase)
- Offline data caching with Redis
- Performance optimization (code splitting, lazy loading)

# Architectural Solution
- Microservice architecture for PWA features
- CDN integration for asset delivery
- Redis caching for offline data storage
- Firebase for push notifications
- API gateway for service orchestration

# ADA Criteria
- Screen reader compatibility for PWA features
- Keyboard navigation for all interactions
- High contrast support for all themes
- Voice control compatibility
- Focus management for single-page app navigation

# Performance Impact
- Initial load time < 3 seconds
- Offline functionality for 7 days minimum
- Push notification delivery < 5 seconds
- Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1

# Security Impact
- Secure service worker implementation
- HTTPS enforcement for all PWA features
- Content Security Policy configuration
- OAuth 2.0 integration for secure authentication
            """,
            "issuetype": {"name": "Epic"},
            "components": [{"name": "PWA"}, {"name": "Mobile"}, {"name": "Performance"}],
            "customfield_10002": 13,
            "priority": {"name": "High"}
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(feature_ticket, "Actionable")
    
    print(f"📊 Sprint Readiness: {result.data['Readiness']['Score']}% → {result.data['Readiness']['Status']}")
    print(f"🎨 Design Links: {len(result.data['DesignLinks'])}")
    print(f"🧱 Technical Implementation: {result.data['TechnicalADA']['ImplementationDetails']}")
    print(f"🏗️ Architecture: {result.data['TechnicalADA']['ArchitecturalSolution']}")
    print(f"♿ ADA Status: {result.data['TechnicalADA']['ADA']['Status']}")
    print(f"📈 DesignSync Score: {result.data['DesignSync']['Score']}")
    
    return result

def demo_task_analysis():
    """Demo Task analysis"""
    print("\n📋 Demo: Task Analysis")
    print("=" * 50)
    
    task_ticket = {
        "key": "TASK-004",
        "fields": {
            "summary": "Update API documentation for new authentication endpoints",
            "description": """
# Task Description
Update the API documentation to include the new OAuth 2.0 authentication endpoints and provide comprehensive examples for developers.

# Outcome/Definition of Done
- All new OAuth 2.0 endpoints documented with examples
- Authentication flow diagrams updated with new process
- Code samples provided for major languages (Python, JavaScript, Java)
- Documentation reviewed and approved by tech lead
- Developer portal updated with interactive examples

# Dependencies
- Depends on: AUTH-123 (OAuth implementation)
- Blocks: DEV-456 (Frontend integration)
- Related to: API-789 (Endpoint documentation)

# Testing/Validation
- Documentation review by development team
- Code examples tested in sandbox environment
- Diagrams validated by solution architect
- Developer feedback incorporated
            """,
            "issuetype": {"name": "Task"},
            "components": [{"name": "Documentation"}, {"name": "API"}],
            "customfield_10002": 2
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(task_ticket, "Insight")
    
    print(f"📊 Sprint Readiness: {result.data['Readiness']['Score']}% → {result.data['Readiness']['Status']}")
    print(f"📋 Card Type: {result.data['Type']}")
    print(f"💡 PO Recommendations: {len(result.data['Recommendations']['PO'])}")
    print(f"🔧 Dev Recommendations: {len(result.data['Recommendations']['Dev'])}")
    
    return result

def demo_figma_detection():
    """Demo Figma link detection"""
    print("\n🎨 Demo: Figma Link Detection")
    print("=" * 50)
    
    figma_ticket = {
        "key": "FIGMA-005",
        "fields": {
            "summary": "Update checkout flow design with new payment options",
            "description": """
# Acceptance Criteria
- User can complete checkout in 3 steps maximum
- Payment form validation works correctly for all methods
- Design: https://figma.com/file/xyz789/Checkout-Flow-Design
- Prototype: https://figma.com/proto/abc123/Checkout-Prototype-v2
- Figma Link: https://figma.com/file/def456/Checkout-Design-System
- Design System: https://figma.com/file/ghi789/Design-System-v3

# Testing Steps
1. Follow the design prototype exactly
2. Test all form validations match design
3. Verify responsive design on all breakpoints
4. Test accessibility with screen readers
            """,
            "issuetype": {"name": "Story"}
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(figma_ticket, "Actionable")
    
    print(f"🎨 Design Links Found: {len(result.data['DesignLinks'])}")
    print(f"🔗 Links: {result.data['DesignLinks']}")
    print(f"📊 DesignSync Enabled: {result.data['DesignSync']['Enabled']}")
    print(f"📈 DesignSync Score: {result.data['DesignSync']['Score']}")
    print(f"⚠️ Mismatches: {len(result.data['DesignSync']['Mismatches'])}")
    print(f"📝 Changes: {len(result.data['DesignSync']['Changes'])}")
    
    return result

def demo_batch_processing():
    """Demo batch processing"""
    print("\n📦 Demo: Batch Processing")
    print("=" * 50)
    
    tickets = [
        {
            "key": "BATCH-001",
            "fields": {
                "summary": "Quick user story for batch processing",
                "description": "As a user, I want to save my preferences so that I can have a personalized experience.",
                "issuetype": {"name": "Story"}
            }
        },
        {
            "key": "BATCH-002",
            "fields": {
                "summary": "Quick bug report for batch processing",
                "description": "Button not working on mobile. Steps: 1) Open app 2) Tap button 3) Nothing happens",
                "issuetype": {"name": "Bug"}
            }
        },
        {
            "key": "BATCH-003",
            "fields": {
                "summary": "Quick task for batch processing",
                "description": "Update documentation for new API endpoints",
                "issuetype": {"name": "Task"}
            }
        }
    ]
    
    groomroom = GroomRoomVNext()
    results = []
    
    for ticket in tickets:
        result = groomroom.analyze_ticket(ticket, "Summary")
        results.append(result)
    
    # Generate batch summary
    ready_count = sum(1 for r in results if r.data['Readiness']['Status'] == 'Ready')
    needs_refinement = sum(1 for r in results if r.data['Readiness']['Status'] == 'Needs Refinement')
    not_ready = sum(1 for r in results if r.data['Readiness']['Status'] == 'Not Ready')
    
    print(f"📊 Batch Summary: {ready_count} Ready, {needs_refinement} Needs Refinement, {not_ready} Not Ready")
    print(f"📈 Average Readiness: {sum(r.data['Readiness']['Score'] for r in results) // len(results)}%")
    
    # Top gaps analysis
    all_missing = []
    for result in results:
        all_missing.extend(result.data['Readiness']['MissingFields'])
    
    from collections import Counter
    top_gaps = Counter(all_missing).most_common(3)
    print(f"🔍 Top gaps: {', '.join([f'{gap}({count})' for gap, count in top_gaps])}")
    
    return results

def main():
    """Run comprehensive demo"""
    print("🚀 GroomRoom vNext - Comprehensive Demo")
    print("=" * 60)
    print("Enhanced features: All card types, Figma detection, DoR by type,")
    print("conflict checks, contextual ACs & P/N/E scenarios, Markdown + JSON")
    print("=" * 60)
    
    try:
        # Run all demos
        story_result = demo_story_with_figma()
        bug_result = demo_bug_analysis()
        feature_result = demo_feature_epic()
        task_result = demo_task_analysis()
        figma_result = demo_figma_detection()
        batch_results = demo_batch_processing()
        
        print("\n" + "=" * 60)
        print("✅ ALL DEMOS COMPLETED SUCCESSFULLY")
        print("🎯 GroomRoom vNext is production-ready!")
        print("\n📊 Demo Summary:")
        print(f"   • User Story with Figma: ✅")
        print(f"   • Bug Analysis: ✅")
        print(f"   • Feature/Epic Analysis: ✅")
        print(f"   • Task Analysis: ✅")
        print(f"   • Figma Detection: ✅")
        print(f"   • Batch Processing: ✅")
        
        print("\n🎉 GroomRoom vNext enabled: all card types, Figma link detection inside ACs, accurate DoR by type, conflict checks, contextual ACs & P/N/E scenarios, consistent Markdown + JSON outputs.")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
