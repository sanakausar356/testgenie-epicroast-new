#!/usr/bin/env python3
"""
Simple test for enhanced GroomRoom functionality
"""

def test_import():
    """Test if we can import the enhanced GroomRoom"""
    try:
        from groomroom.core import GroomRoom
        print("✅ GroomRoom import successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic GroomRoom functionality"""
    try:
        from groomroom.core import GroomRoom
        
        # Initialize GroomRoom
        groomroom = GroomRoom()
        print("✅ GroomRoom initialization successful")
        
        # Test ticket data
        test_ticket = {
            'key': 'TEST-123',
            'summary': 'As a customer, I want to apply discount codes during checkout',
            'description': 'This feature allows customers to apply discount codes during checkout.',
            'acceptance_criteria': [
                'User can enter a discount code',
                'System validates the code',
                'Discount is applied to total price'
            ],
            'issuetype': {'name': 'Story'},
            'status': {'name': 'To Do'},
            'priority': {'name': 'Medium'},
            'assignee': None,
            'reporter': {'displayName': 'Product Owner'},
            'created': '2024-01-15T10:00:00.000+0000',
            'updated': '2024-01-15T10:00:00.000+0000',
            'project': {'name': 'E-commerce Platform'},
            'labels': ['enhancement'],
            'components': [{'name': 'Frontend'}]
        }
        
        # Test analysis
        result = groomroom.analyze_ticket(test_ticket, mode="actionable")
        
        if "error" in result:
            print(f"❌ Analysis error: {result['error']}")
            return False
        
        print("✅ Ticket analysis successful")
        print(f"📊 Sprint Readiness: {result.get('Readiness', {}).get('Score', 'N/A')}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Enhanced GroomRoom")
    print("=" * 40)
    
    # Test import
    if not test_import():
        exit(1)
    
    # Test basic functionality
    if not test_basic_functionality():
        exit(1)
    
    print("\n🎉 All tests passed!")
