#!/usr/bin/env python3
"""
Test script to verify TestGenie installation and configuration
"""

import sys
import os
from dotenv import load_dotenv

def test_imports():
    """Test if all required packages can be imported"""
    print("Testing imports...")
    
    try:
        import click
        print("✅ click imported successfully")
    except ImportError as e:
        print(f"❌ click import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
        return False
    
    try:
        from rich.console import Console
        print("✅ rich imported successfully")
    except ImportError as e:
        print(f"❌ rich import failed: {e}")
        return False
    
    try:
        from prompt_toolkit import PromptSession
        print("✅ prompt_toolkit imported successfully")
    except ImportError as e:
        print(f"❌ prompt_toolkit import failed: {e}")
        return False
    
    return True

def test_env_config():
    """Test if environment variables are properly configured"""
    print("\nTesting environment configuration...")
    
    load_dotenv()
    
    required_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY',
        'AZURE_OPENAI_DEPLOYMENT_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var} is configured")
        else:
            print(f"❌ {var} is missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please copy env.example to env.local.env and fill in your Azure OpenAI credentials")
        return False
    
    return True

def test_azure_connection():
    """Test Azure OpenAI connection"""
    print("\nTesting Azure OpenAI connection...")
    
    try:
        import openai
        from dotenv import load_dotenv
        
        load_dotenv()
        
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        )
        
        # Test with a simple prompt
        response = client.chat.completions.create(
            model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            messages=[
                {"role": "user", "content": "Say 'TestGenie is working!' if you can read this."}
            ],
            max_completion_tokens=50
        )
        
        print("✅ Azure OpenAI connection successful")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Azure OpenAI connection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 TestGenie Installation Test")
    print("=" * 40)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import test failed. Please install dependencies:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    # Test environment configuration
    if not test_env_config():
        print("\n❌ Environment configuration test failed.")
        sys.exit(1)
    
    # Test Azure connection
    if not test_azure_connection():
        print("\n❌ Azure OpenAI connection test failed.")
        sys.exit(1)
    
    print("\n🎉 All tests passed! TestGenie is ready to use.")
    print("\nYou can now run:")
    print("- python testgenie.py")
    print("- python -m testgenie.cli")
    print("- testgenie (if installed with pip install -e .)")

if __name__ == '__main__':
    main() 