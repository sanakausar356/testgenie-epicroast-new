#!/usr/bin/env python3
"""
Script to check .env file configuration without exposing sensitive data
"""

import os
from dotenv import load_dotenv

def check_env_config():
    """Check if .env file is properly configured"""
    print("🔍 Checking .env file configuration...")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your Azure OpenAI credentials")
        return False
    
    print("✅ .env file found")
    
    # Load environment variables
    load_dotenv()
    
    # Check each required variable
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY', 
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first few characters to verify it's not placeholder
            preview = value[:10] + "..." if len(value) > 10 else value
            if "your" in value.lower() or "placeholder" in value.lower():
                print(f"❌ {var}: Contains placeholder text")
                all_good = False
            else:
                print(f"✅ {var}: {preview}")
        else:
            print(f"❌ {var}: Missing")
            all_good = False
    
    # Check endpoint format
    endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
    if endpoint:
        if not endpoint.startswith('https://'):
            print("⚠️  AZURE_OPENAI_ENDPOINT should start with 'https://'")
        if not endpoint.endswith('/'):
            print("⚠️  AZURE_OPENAI_ENDPOINT should end with '/'")
    
    # Check API key format
    api_key = os.getenv('AZURE_OPENAI_API_KEY')
    if api_key:
        if not api_key.startswith('sk-'):
            print("⚠️  AZURE_OPENAI_API_KEY should start with 'sk-'")
    
    print("\n" + "=" * 50)
    
    if all_good:
        print("🎉 .env file looks good!")
        print("You can now run: python test_installation.py")
    else:
        print("❌ Please fix the issues above")
        print("Make sure to use your actual Azure OpenAI credentials, not placeholder text")
    
    return all_good

if __name__ == "__main__":
    check_env_config() 