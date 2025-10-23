"""
Simple test for GroomRoom vNext
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from groomroom.core_vnext import GroomRoomVNext
    print("✅ Import successful")
    
    # Test basic functionality
    groomroom = GroomRoomVNext()
    print("✅ GroomRoom instance created")
    
    # Test with simple ticket
    simple_ticket = {
        "key": "TEST-001",
        "fields": {
            "summary": "Test ticket",
            "description": "Simple test description",
            "issuetype": {"name": "Story"}
        }
    }
    
    result = groomroom.analyze_ticket(simple_ticket, "Actionable")
    print("✅ Analysis completed")
    print(f"📊 Result type: {type(result)}")
    print(f"📋 Ticket key: {result.data.get('TicketKey', 'Unknown')}")
    print(f"📈 Readiness: {result.data.get('Readiness', {}).get('Score', 0)}%")
    
    print("\n🎉 GroomRoom vNext basic test passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
