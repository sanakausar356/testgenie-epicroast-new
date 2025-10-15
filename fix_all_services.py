#!/usr/bin/env python3
"""
Comprehensive fix script for all services (EpicRoast, GroomRoom, TestGenie)
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment_variables():
    """Check all required environment variables"""
    print("=== Environment Variables Check ===")
    
    # Azure OpenAI variables (required for all services)
    azure_vars = {
        'AZURE_OPENAI_ENDPOINT': 'Azure OpenAI endpoint URL',
        'AZURE_OPENAI_API_KEY': 'Azure OpenAI API key',
        'AZURE_OPENAI_DEPLOYMENT_NAME': 'Azure OpenAI deployment name',
        'AZURE_OPENAI_API_VERSION': 'Azure OpenAI API version (optional, defaults to 2024-02-15-preview)'
    }
    
    # Jira variables (optional but recommended)
    jira_vars = {
        'JIRA_SERVER_URL': 'Jira server URL',
        'JIRA_EMAIL': 'Jira email',
        'JIRA_API_TOKEN': 'Jira API token'
    }
    
    # Teams variables (optional)
    teams_vars = {
        'TEAMS_WEBHOOK_URL': 'Microsoft Teams webhook URL'
    }
    
    all_vars = {**azure_vars, **jira_vars, **teams_vars}
    
    missing_critical = []
    missing_optional = []
    
    for var, description in all_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'TOKEN' in var:
                display_value = value[:8] + '***' if len(value) > 8 else '***'
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            if var in azure_vars:
                missing_critical.append(var)
                print(f"❌ {var}: MISSING (CRITICAL)")
            else:
                missing_optional.append(var)
                print(f"⚠️  {var}: MISSING (Optional)")
    
    return missing_critical, missing_optional

def test_individual_services():
    """Test each service individually"""
    print("\n=== Individual Service Tests ===")
    
    # Test TestGenie
    print("\n🧪 Testing TestGenie...")
    try:
        from testgenie.core import TestGenie
        testgenie = TestGenie()
        if testgenie.client:
            print("✅ TestGenie: Azure OpenAI client working")
        else:
            print("❌ TestGenie: Azure OpenAI client not available")
    except Exception as e:
        print(f"❌ TestGenie error: {e}")
    
    # Test EpicRoast
    print("\n🔥 Testing EpicRoast...")
    try:
        from epicroast.core import EpicRoast
        epicroast = EpicRoast()
        if epicroast.client:
            print("✅ EpicRoast: Azure OpenAI client working")
        else:
            print("❌ EpicRoast: Azure OpenAI client not available")
    except Exception as e:
        print(f"❌ EpicRoast error: {e}")
    
    # Test GroomRoom
    print("\n🧹 Testing GroomRoom...")
    try:
        from groomroom.core import GroomRoom
        groomroom = GroomRoom()
        if groomroom.client:
            print("✅ GroomRoom: Azure OpenAI client working")
        else:
            print("❌ GroomRoom: Azure OpenAI client not available")
    except Exception as e:
        print(f"❌ GroomRoom error: {e}")
    
    # Test Jira Integration
    print("\n🔗 Testing Jira Integration...")
    try:
        from jira_integration import JiraIntegration
        jira = JiraIntegration()
        if jira.is_available():
            print("✅ Jira Integration: Working")
        else:
            print("❌ Jira Integration: Not available")
    except Exception as e:
        print(f"❌ Jira Integration error: {e}")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n=== API Endpoint Tests ===")
    
    try:
        import requests
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health endpoint working")
            print(f"Services status: {data.get('services', {})}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to localhost:5000 - Flask app not running")
    except Exception as e:
        print(f"❌ API test error: {e}")

def create_env_template():
    """Create a template .env file"""
    print("\n=== Environment Variables Template ===")
    
    template = """# Azure OpenAI Configuration (REQUIRED for all services)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Jira Configuration (Optional but recommended)
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_EMAIL=your_email@domain.com
JIRA_API_TOKEN=your_jira_api_token_here

# Microsoft Teams Configuration (Optional)
TEAMS_WEBHOOK_URL=your_teams_webhook_url_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
"""
    
    print("Create a .env file in the root directory with these variables:")
    print(template)
    
    return template

def provide_fix_instructions(missing_critical, missing_optional):
    """Provide specific fix instructions"""
    print("\n=== Fix Instructions ===")
    
    if missing_critical:
        print("🚨 CRITICAL ISSUES TO FIX:")
        print("The following Azure OpenAI variables are required for all services to work:")
        for var in missing_critical:
            print(f"  - {var}")
        
        print("\n📋 Steps to fix:")
        print("1. Create a .env file in the root directory")
        print("2. Add the missing Azure OpenAI variables")
        print("3. Get your Azure OpenAI credentials from:")
        print("   https://portal.azure.com -> Azure OpenAI -> Your resource")
        print("4. Restart the Flask app")
        
    if missing_optional:
        print("\n⚠️  OPTIONAL IMPROVEMENTS:")
        print("These variables will enhance functionality:")
        for var in missing_optional:
            print(f"  - {var}")
    
    if not missing_critical:
        print("✅ All critical environment variables are set!")
        print("If services still don't work, check the Azure OpenAI configuration.")

def main():
    """Main diagnostic and fix process"""
    print("=== TestGenie, EpicRoast, GroomRoom Service Fix ===")
    
    # Check environment variables
    missing_critical, missing_optional = check_environment_variables()
    
    # Test individual services
    test_individual_services()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Provide fix instructions
    provide_fix_instructions(missing_critical, missing_optional)
    
    # Create template
    create_env_template()
    
    print("\n=== Summary ===")
    if missing_critical:
        print("❌ Services will NOT work without Azure OpenAI configuration")
        print("Please set the missing environment variables and restart the app")
    else:
        print("✅ Environment variables look good")
        print("If services still don't work, check the individual service logs above")

if __name__ == "__main__":
    main()
