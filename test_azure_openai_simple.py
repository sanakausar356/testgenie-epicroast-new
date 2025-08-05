#!/usr/bin/env python3
"""
Simple test to isolate Azure OpenAI client initialization issue
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_openai_simple():
    """Test simple Azure OpenAI client creation"""
    print("🔍 Testing Azure OpenAI client creation...")
    
    try:
        import openai
        
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        api_version = os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        
        print(f"✅ Environment variables loaded:")
        print(f"   - Endpoint: {'*' * len(endpoint) if endpoint else 'Not set'}")
        print(f"   - API Key: {'*' * len(api_key) if api_key else 'Not set'}")
        print(f"   - API Version: {api_version}")
        print(f"   - Deployment: {'*' * len(deployment_name) if deployment_name else 'Not set'}")
        
        # Test client creation with minimal parameters
        print("\n📝 Creating Azure OpenAI client...")
        client = openai.AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        print("✅ Azure OpenAI client created successfully!")
        
        # Test a simple call
        print("\n📝 Testing simple API call...")
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "user", "content": "Say 'Hello World'"}
            ],
            max_completion_tokens=50
        )
        
        result = response.choices[0].message.content
        print(f"✅ API call successful: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_openai_version():
    """Check OpenAI library version"""
    print("\n🔍 Checking OpenAI library version...")
    
    try:
        import openai
        print(f"✅ OpenAI library version: {openai.__version__}")
        
        # Check if we can access the AzureOpenAI class
        print(f"✅ AzureOpenAI class available: {hasattr(openai, 'AzureOpenAI')}")
        
    except Exception as e:
        print(f"❌ Error checking OpenAI version: {e}")

if __name__ == '__main__':
    print("🧪 Azure OpenAI Simple Test")
    print("=" * 40)
    
    test_openai_version()
    success = test_azure_openai_simple()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!") 