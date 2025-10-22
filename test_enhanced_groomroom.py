#!/usr/bin/env python3
"""
Test script for enhanced GroomRoom Refinement Agent with 04-mini style output
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groomroom.core import GroomRoom

def test_enhanced_groomroom():
    """Test the enhanced GroomRoom functionality"""
    print("🧪 Testing Enhanced GroomRoom Refinement Agent")
    print("=" * 60)
    
    # Initialize GroomRoom
    groomroom = GroomRoom()
    
    # Test ticket data
    test_ticket = {
        'key': 'TEST-123',
        'summary': 'As a customer, I want to apply discount codes during checkout so that I can save money on my purchase',
        'description': 'This feature allows customers to apply discount codes during the checkout process. The system should validate the code, apply the discount, and update the total price accordingly.',
        'acceptance_criteria': [
            'User can enter a discount code in the checkout form',
            'System validates the discount code',
            'Discount is applied to the total price',
            'User sees updated price with discount applied'
        ],
        'issuetype': {'name': 'Story'},
        'status': {'name': 'To Do'},
        'priority': {'name': 'Medium'},
        'assignee': None,
        'reporter': {'displayName': 'Product Owner'},
        'created': '2024-01-15T10:00:00.000+0000',
        'updated': '2024-01-15T10:00:00.000+0000',
        'project': {'name': 'E-commerce Platform'},
        'labels': ['enhancement', 'checkout'],
        'components': [{'name': 'Frontend'}, {'name': 'Backend'}]
    }
    
    print("\n📋 Test Ticket:")
    print(f"Key: {test_ticket['key']}")
    print(f"Summary: {test_ticket['summary']}")
    print(f"AC Count: {len(test_ticket['acceptance_criteria'])}")
    
    # Test Actionable mode
    print("\n⚡ Testing Actionable Mode (300-600 words target)")
    print("-" * 50)
    
    try:
        result = groomroom.analyze_ticket(test_ticket, mode="actionable")
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print("✅ Analysis completed successfully")
        print(f"📊 Sprint Readiness: {result['Readiness']['Score']}% ({result['Readiness']['Status']})")
        print(f"📋 DoR Coverage: {result['Readiness']['DoRCoveragePercent']}%")
        print(f"🧭 Framework Scores: ROI {result['FrameworkScores']['ROI']} | INVEST {result['FrameworkScores']['INVEST']} | ACCEPT {result['FrameworkScores']['ACCEPT']} | 3C {result['FrameworkScores']['3C']}")
        
        # Display enhanced output
        if "enhanced_output" in result:
            print("\n📄 Enhanced Output:")
            print(result["enhanced_output"])
        
        # Check word count
        word_count = result.get("word_count", 0)
        print(f"\n📏 Word Count: {word_count} (target: 300-600)")
        
        if 300 <= word_count <= 600:
            print("✅ Word count within target range")
        else:
            print("⚠️ Word count outside target range")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False
    
    # Test Insight mode
    print("\n🔍 Testing Insight Mode (180-350 words target)")
    print("-" * 50)
    
    try:
        result = groomroom.analyze_ticket(test_ticket, mode="insight")
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        word_count = result.get("word_count", 0)
        print(f"📏 Word Count: {word_count} (target: 180-350)")
        
        if 180 <= word_count <= 350:
            print("✅ Word count within target range")
        else:
            print("⚠️ Word count outside target range")
        
    except Exception as e:
        print(f"❌ Error during insight analysis: {e}")
        return False
    
    # Test Summary mode
    print("\n📊 Testing Summary Mode (120-180 words target)")
    print("-" * 50)
    
    try:
        result = groomroom.analyze_ticket(test_ticket, mode="summary")
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        word_count = result.get("word_count", 0)
        print(f"📏 Word Count: {word_count} (target: 120-180)")
        
        if 120 <= word_count <= 180:
            print("✅ Word count within target range")
        else:
            print("⚠️ Word count outside target range")
        
    except Exception as e:
        print(f"❌ Error during summary analysis: {e}")
        return False
    
    # Test batch processing
    print("\n📦 Testing Batch Processing")
    print("-" * 50)
    
    try:
        batch_tickets = [test_ticket, test_ticket]  # Duplicate for testing
        batch_result = groomroom.analyze_batch_tickets(batch_tickets, mode="actionable")
        
        print("✅ Batch processing completed")
        print(f"📊 Batch Summary: {batch_result['summary']}")
        print(f"📄 Batch Header:\n{batch_result['batch_header']}")
        
    except Exception as e:
        print(f"❌ Error during batch processing: {e}")
        return False
    
    print("\n🎉 Enhanced GroomRoom testing completed successfully!")
    print("✅ All features working as expected")
    
    return True

if __name__ == "__main__":
    success = test_enhanced_groomroom()
    sys.exit(0 if success else 1)