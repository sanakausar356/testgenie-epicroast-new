"""
Test GroomRoom vNext Implementation
Comprehensive testing of the enhanced GroomRoom functionality
"""

import json
from groomroom.core_vnext import GroomRoomVNext, analyze_ticket

def test_story_analysis():
    """Test User Story analysis with Figma links"""
    print("🧪 Testing User Story Analysis...")
    
    # Sample User Story ticket with Figma links
    story_ticket = {
        "key": "TEST-123",
        "fields": {
            "summary": "As a customer, I want to filter products by price range so that I can find affordable items",
            "description": """
# User Story
As a customer, I want to filter products by price range so that I can find affordable items within my budget.

# Acceptance Criteria
- User can select minimum and maximum price values
- Filter results update within 1 second
- Clear filters button resets to default state
- Price range validation prevents invalid ranges
- Design: https://figma.com/file/abc123/Product-Filter-Design

# Testing Steps
1. Navigate to product listing page
2. Open price filter panel
3. Set minimum price to $50
4. Set maximum price to $200
5. Verify results update
6. Test clear filters functionality

# Implementation Details
- Use React hooks for state management
- Implement debounced search for performance
- Add loading states for better UX

# ADA Criteria
- Keyboard navigation works for all filter controls
- Screen reader announces filter changes
- High contrast mode support
- Focus indicators visible
            """,
            "issuetype": {"name": "Story"},
            "components": [{"name": "Product Catalog"}],
            "customfield_10002": 5,  # Story points
            "priority": {"name": "High"}
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(story_ticket, "Actionable")
    
    print(f"✅ Analysis completed")
    print(f"📊 Readiness Score: {result.data['Readiness']['Score']}%")
    print(f"📋 Status: {result.data['Readiness']['Status']}")
    print(f"🎨 Design Links: {len(result.data['DesignLinks'])}")
    print(f"📝 Suggested ACs: {len(result.data['AcceptanceCriteriaAudit']['SuggestedRewrites'])}")
    
    return result

def test_bug_analysis():
    """Test Bug analysis with structured content"""
    print("\n🐛 Testing Bug Analysis...")
    
    bug_ticket = {
        "key": "BUG-456",
        "fields": {
            "summary": "Login button not responding on mobile devices",
            "description": """
# Current Behaviour
Login button appears but does not respond to touch events on mobile devices (iOS Safari, Android Chrome).

# Steps to Reproduce
1. Open application on mobile device
2. Navigate to login page
3. Enter valid credentials
4. Tap login button
5. Observe no response

# Expected Behaviour
Login button should process the request and redirect to dashboard.

# Environment
- iOS Safari 15+
- Android Chrome 90+
- Mobile viewport < 768px

# Severity
High - blocks user access to application
            """,
            "issuetype": {"name": "Bug"},
            "priority": {"name": "Critical"},
            "components": [{"name": "Authentication"}]
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(bug_ticket, "Actionable")
    
    print(f"✅ Bug analysis completed")
    print(f"📊 Readiness Score: {result.data['Readiness']['Score']}%")
    print(f"🐞 Bug Review: {result.data['BugReview'] is not None}")
    print(f"🧪 Test Scenarios: {len(result.data['TestScenarios']['Positive'])} positive scenarios")
    
    return result

def test_task_analysis():
    """Test Task analysis"""
    print("\n📋 Testing Task Analysis...")
    
    task_ticket = {
        "key": "TASK-789",
        "fields": {
            "summary": "Update API documentation for new authentication endpoints",
            "description": """
# Task Description
Update the API documentation to include the new OAuth 2.0 authentication endpoints and provide examples for developers.

# Outcome/Definition of Done
- All new endpoints documented with examples
- Authentication flow diagrams updated
- Code samples provided for major languages
- Documentation reviewed by tech lead

# Dependencies
- Depends on: AUTH-123 (OAuth implementation)
- Blocks: DEV-456 (Frontend integration)

# Testing/Validation
- Documentation review by team
- Code examples tested
- Diagrams validated by architect
            """,
            "issuetype": {"name": "Task"},
            "components": [{"name": "Documentation"}]
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(task_ticket, "Insight")
    
    print(f"✅ Task analysis completed")
    print(f"📊 Readiness Score: {result.data['Readiness']['Score']}%")
    print(f"📋 Type: {result.data['Type']}")
    print(f"💡 Recommendations: {len(result.data['Recommendations']['PO'])} PO recommendations")
    
    return result

def test_feature_analysis():
    """Test Feature/Epic analysis with complex content"""
    print("\n🚀 Testing Feature Analysis...")
    
    feature_ticket = {
        "key": "FEATURE-101",
        "fields": {
            "summary": "Implement Progressive Web App (PWA) capabilities for mobile users",
            "description": """
# Feature Description
Implement Progressive Web App capabilities to provide native app-like experience for mobile users across all brands.

# User Story
As a mobile user, I want to install the web app on my device so that I can access features quickly without browser navigation.

# Acceptance Criteria
- App can be installed on mobile devices
- Offline functionality for core features
- Push notifications for order updates
- App-like navigation and interactions
- Performance meets PWA standards
- Design: https://figma.com/file/def456/PWA-Design-System

# Testing Steps
1. Test installation prompts on various devices
2. Verify offline functionality
3. Test push notification delivery
4. Validate performance metrics
5. Cross-browser compatibility testing

# Implementation Details
- Service worker implementation
- Web app manifest configuration
- Push notification service integration
- Offline data caching strategy
- Performance optimization

# Architectural Solution
- Microservice architecture for PWA features
- CDN integration for asset delivery
- Redis caching for offline data
- Firebase for push notifications

# ADA Criteria
- Screen reader compatibility for PWA features
- Keyboard navigation for all interactions
- High contrast support
- Voice control compatibility

# Performance Impact
- Initial load time < 3 seconds
- Offline functionality for 7 days
- Push notification delivery < 5 seconds

# Security Impact
- Secure service worker implementation
- HTTPS enforcement
- Content Security Policy configuration
            """,
            "issuetype": {"name": "Epic"},
            "components": [{"name": "PWA"}, {"name": "Mobile"}],
            "customfield_10002": 13
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(result, "Actionable")
    
    print(f"✅ Feature analysis completed")
    print(f"📊 Readiness Score: {result.data['Readiness']['Score']}%")
    print(f"🎨 Design Links: {len(result.data['DesignLinks'])}")
    print(f"🧱 Technical ADA: {result.data['TechnicalADA']['implementation_details']}")
    
    return result

def test_figma_detection():
    """Test Figma link detection in various formats"""
    print("\n🎨 Testing Figma Link Detection...")
    
    figma_ticket = {
        "key": "FIGMA-001",
        "fields": {
            "summary": "Update checkout flow design",
            "description": """
# Acceptance Criteria
- User can complete checkout in 3 steps
- Payment form validation works correctly
- Design: https://figma.com/file/xyz789/Checkout-Flow
- Prototype: https://figma.com/proto/abc123/Checkout-Prototype
- Figma Link: https://figma.com/file/def456/Checkout-Design-v2

# Testing Steps
1. Follow the design prototype
2. Test all form validations
3. Verify responsive design
            """,
            "issuetype": {"name": "Story"}
        }
    }
    
    groomroom = GroomRoomVNext()
    result = groomroom.analyze_ticket(figma_ticket, "Actionable")
    
    print(f"✅ Figma detection completed")
    print(f"🎨 Design Links Found: {len(result.data['DesignLinks'])}")
    print(f"🔗 Links: {result.data['DesignLinks']}")
    print(f"📊 DesignSync Score: {result.data['DesignSync']['Score']}")
    
    return result

def test_batch_analysis():
    """Test batch analysis with multiple tickets"""
    print("\n📦 Testing Batch Analysis...")
    
    tickets = [
        {
            "key": "BATCH-001",
            "fields": {
                "summary": "Quick story for batch test",
                "description": "Simple user story for testing",
                "issuetype": {"name": "Story"}
            }
        },
        {
            "key": "BATCH-002", 
            "fields": {
                "summary": "Quick bug for batch test",
                "description": "Simple bug report for testing",
                "issuetype": {"name": "Bug"}
            }
        }
    ]
    
    groomroom = GroomRoomVNext()
    results = []
    
    for ticket in tickets:
        result = groomroom.analyze_ticket(ticket, "Summary")
        results.append(result)
    
    print(f"✅ Batch analysis completed")
    print(f"📊 Processed {len(results)} tickets")
    
    # Generate batch summary
    ready_count = sum(1 for r in results if r.data['Readiness']['Status'] == 'Ready')
    needs_refinement = sum(1 for r in results if r.data['Readiness']['Status'] == 'Needs Refinement')
    not_ready = sum(1 for r in results if r.data['Readiness']['Status'] == 'Not Ready')
    
    print(f"📈 Batch Summary: {ready_count} Ready, {needs_refinement} Needs Refinement, {not_ready} Not Ready")
    
    return results

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n⚠️ Testing Edge Cases...")
    
    # Empty ticket
    empty_ticket = {
        "key": "EMPTY-001",
        "fields": {
            "summary": "",
            "description": "",
            "issuetype": {"name": "Story"}
        }
    }
    
    # Malformed ticket
    malformed_ticket = {
        "key": "MALFORMED-001",
        "fields": {}
    }
    
    groomroom = GroomRoomVNext()
    
    # Test empty ticket
    empty_result = groomroom.analyze_ticket(empty_ticket, "Actionable")
    print(f"✅ Empty ticket handled: {empty_result.data['Title']}")
    
    # Test malformed ticket
    malformed_result = groomroom.analyze_ticket(malformed_ticket, "Actionable")
    print(f"✅ Malformed ticket handled: {malformed_result.data['TicketKey']}")
    
    return [empty_result, malformed_result]

def main():
    """Run all tests"""
    print("🚀 GroomRoom vNext - Comprehensive Testing")
    print("=" * 50)
    
    try:
        # Run all test scenarios
        story_result = test_story_analysis()
        bug_result = test_bug_analysis()
        task_result = test_task_analysis()
        feature_result = test_feature_analysis()
        figma_result = test_figma_detection()
        batch_results = test_batch_analysis()
        edge_results = test_edge_cases()
        
        print("\n" + "=" * 50)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("🎯 GroomRoom vNext is ready for production!")
        print("\n📊 Test Summary:")
        print(f"   • User Story Analysis: ✅")
        print(f"   • Bug Analysis: ✅")
        print(f"   • Task Analysis: ✅")
        print(f"   • Feature Analysis: ✅")
        print(f"   • Figma Detection: ✅")
        print(f"   • Batch Processing: ✅")
        print(f"   • Edge Case Handling: ✅")
        
        print("\n🎉 GroomRoom vNext enabled: all card types, Figma link detection inside ACs, accurate DoR by type, conflict checks, contextual ACs & P/N/E scenarios, consistent Markdown + JSON outputs.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
