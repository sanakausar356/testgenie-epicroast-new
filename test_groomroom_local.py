#!/usr/bin/env python3
"""
Local test script for GroomRoom functionality
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_groomroom():
    """Test GroomRoom functionality"""
    try:
        print("Testing GroomRoom initialization...")
        from groomroom.core import GroomRoom
        
        groomroom = GroomRoom()
        print("✅ GroomRoom initialized successfully")
        
        # Test with sample ticket content
        sample_ticket = """
        As a user, I want to be able to click a button to submit a form
        so that I can complete my registration process.
        
        Acceptance Criteria:
        - User can click the submit button
        - Form validation occurs before submission
        - Success message is displayed after submission
        - Error handling for network issues
        """
        
        print("\nTesting groom analysis generation...")
        result = groomroom.generate_concise_groom_analysis(sample_ticket)
        
        if result:
            print("✅ Groom analysis generated successfully")
            print(f"Result length: {len(result)} characters")
            print("\nFirst 200 characters:")
            print(result[:200] + "..." if len(result) > 200 else result)
        else:
            print("❌ Groom analysis generation failed - empty result")
            
    except Exception as e:
        print(f"❌ Error testing GroomRoom: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_backend_imports():
    """Test that backend can import all required modules"""
    try:
        print("\nTesting backend imports...")
        
        # Test imports that the backend uses
        from testgenie.core import TestGenie
        print("✅ TestGenie import successful")
        
        from epicroast.core import EpicRoast
        print("✅ EpicRoast import successful")
        
        from groomroom.core import GroomRoom
        print("✅ GroomRoom import successful")
        
        from jira_integration import JiraIntegration
        print("✅ JiraIntegration import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== GroomRoom Local Test ===")
    
    # Test backend imports first
    if not test_backend_imports():
        print("\n❌ Backend imports failed. Cannot proceed with GroomRoom test.")
        sys.exit(1)
    
    # Test GroomRoom functionality
    if test_groomroom():
        print("\n✅ All tests passed! GroomRoom is working correctly.")
    else:
        print("\n❌ GroomRoom test failed.")
        sys.exit(1)
