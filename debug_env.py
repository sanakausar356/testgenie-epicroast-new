#!/usr/bin/env python3
"""
Debug script to check .env file contents
"""

import os

def debug_env():
    """Debug .env file issues"""
    print("🔍 Debugging .env file...")
    print("=" * 50)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # List all files
    print("\nFiles in current directory:")
    for file in os.listdir('.'):
        if file.startswith('.') or file.endswith('.env'):
            print(f"  {file}")
    
    # Check if .env exists
    env_path = '.env'
    if os.path.exists(env_path):
        print(f"\n✅ .env file exists at: {os.path.abspath(env_path)}")
        
        # Read and show contents (masking sensitive parts)
        try:
            with open(env_path, 'r') as f:
                lines = f.readlines()
            
            print(f"\n📄 .env file contents ({len(lines)} lines):")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Mask sensitive values
                        if 'KEY' in key.upper():
                            masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
                        else:
                            masked_value = value[:10] + '...' if len(value) > 10 else value
                        print(f"  {i}: {key}={masked_value}")
                    else:
                        print(f"  {i}: {line}")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print(f"\n❌ .env file not found!")
        print("Creating a template .env file...")
        
        # Create template
        template = """AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name_here"""
        
        try:
            with open('.env', 'w') as f:
                f.write(template)
            print("✅ Created .env template file")
            print("Please edit .env file with your actual credentials")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    debug_env() 