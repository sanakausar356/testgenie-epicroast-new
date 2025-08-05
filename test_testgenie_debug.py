#!/usr/bin/env python3
"""
Debug script to test TestGenie functionality
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_testgenie_initialization():
    """Test if TestGenie can be initialized"""
    print("🔍 Testing TestGenie initialization...")
    
    try:
        from testgenie.core import TestGenie
        testgenie = TestGenie()
        print("✅ TestGenie initialized successfully")
        print(f"   - Azure OpenAI client: {'✅ Available' if testgenie.client else '❌ Not available'}")
        return testgenie
    except Exception as e:
        print(f"❌ TestGenie initialization failed: {e}")
        return None

def test_azure_openai_config():
    """Test Azure OpenAI configuration"""
    print("\n🔍 Testing Azure OpenAI configuration...")
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
    
    api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
    print(f"✅ AZURE_OPENAI_API_VERSION: {api_version}")

def test_testgenie_generation(testgenie):
    """Test test scenario generation"""
    print("\n🔍 Testing test scenario generation...")
    
    if not testgenie:
        print("❌ TestGenie not available")
        return
    
    # Sample acceptance criteria
    sample_criteria = """
    As a user, I want to reset my password via email link so that I can regain access to my account.
    
    Acceptance Criteria:
    - User enters email address on password reset page
    - System validates email format and existence
    - System sends password reset link via email
    - User clicks link and is taken to password reset form
    - User enters new password and confirmation
    - System validates password strength and confirmation match
    - System updates password and logs user in
    """
    
    try:
        print("📝 Generating test scenarios for sample acceptance criteria...")
        print(f"   - Input length: {len(sample_criteria)} characters")
        print(f"   - Scenario types: ['positive', 'negative', 'edge']")
        
        # Add detailed debugging
        print("   - Calling generate_test_scenarios...")
        result = testgenie.generate_test_scenarios(sample_criteria, ['positive', 'negative', 'edge'])
        
        print(f"   - Method returned: {type(result)}")
        print(f"   - Result value: {repr(result)}")
        
        if result:
            print("✅ Test scenarios generated successfully!")
            print(f"   - Result length: {len(result)} characters")
            print("   - First 200 characters:")
            print(f"   {result[:200]}...")
            
            # Check if result contains expected sections
            expected_sections = ['Test Scenarios', 'Edge Cases', 'Cross Browser']
            for section in expected_sections:
                if section in result:
                    print(f"   ✅ Contains '{section}' section")
                else:
                    print(f"   ❌ Missing '{section}' section")
        else:
            print("❌ No result returned from generate_test_scenarios")
            print("   - This suggests the method returned None or empty string")
            
    except Exception as e:
        print(f"❌ Error generating test scenarios: {e}")
        import traceback
        traceback.print_exc()

def test_azure_openai_call():
    """Test direct Azure OpenAI call"""
    print("\n🔍 Testing direct Azure OpenAI call...")
    
    try:
        import openai
        
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        client = openai.AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        print("✅ Azure OpenAI client created successfully")
        
        # Test a simple call
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello World'"}
            ],
            max_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ Azure OpenAI call successful: {result}")
        
    except Exception as e:
        print(f"❌ Azure OpenAI call failed: {e}")
        import traceback
        traceback.print_exc()

def test_backend_api():
    """Test backend API endpoint"""
    print("\n🔍 Testing backend API...")
    
    try:
        from backend.app import app
        print("✅ Backend app imported successfully")
        
        # Test if testgenie is available in the app
        with app.app_context():
            # Check if testgenie service is available
            from backend.app import testgenie
            if testgenie:
                print("✅ TestGenie service available in backend")
                print(f"   - Azure OpenAI client: {'✅ Available' if testgenie.client else '❌ Not available'}")
            else:
                print("❌ TestGenie service not available in backend")
                
    except Exception as e:
        print(f"❌ Backend API test failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("🧙‍♂️ TestGenie Debug Script")
    print("=" * 50)
    
    # Test Azure OpenAI configuration
    test_azure_openai_config()
    
    # Test direct Azure OpenAI call
    test_azure_openai_call()
    
    # Test TestGenie initialization
    testgenie = test_testgenie_initialization()
    
    # Test test scenario generation
    test_testgenie_generation(testgenie)
    
    # Test backend API
    test_backend_api()
    
    print("\n" + "=" * 50)
    print("🏁 Debug script completed")

if __name__ == '__main__':
    main() 