"""
Deploy to Railway
"""

import subprocess
import os

def deploy_to_railway():
    """Deploy backend to Railway"""
    print("🚂 Deploying to Railway...")
    
    try:
        # Check if Railway CLI is installed
        try:
            subprocess.run(["railway", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📦 Installing Railway CLI...")
            subprocess.run(["npm", "install", "-g", "@railway/cli"], check=True)
        
        # Login to Railway
        print("🔐 Logging into Railway...")
        subprocess.run(["railway", "login"], check=True)
        
        # Initialize project
        print("🚀 Initializing Railway project...")
        subprocess.run(["railway", "init"], check=True)
        
        # Set environment variables
        print("🔧 Setting environment variables...")
        env_vars = {
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", ""),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", ""),
            "JIRA_URL": os.getenv("JIRA_URL", ""),
            "JIRA_USERNAME": os.getenv("JIRA_USERNAME", ""),
            "JIRA_API_TOKEN": os.getenv("JIRA_API_TOKEN", ""),
            "FLASK_ENV": "production"
        }
        
        for key, value in env_vars.items():
            if value:
                subprocess.run(["railway", "variables", "set", f"{key}={value}"], check=True)
        
        # Deploy
        print("🚀 Deploying to Railway...")
        subprocess.run(["railway", "up"], check=True)
        
        # Get URL
        result = subprocess.run(["railway", "domain"], capture_output=True, text=True, check=True)
        print(f"✅ Successfully deployed to Railway: {result.stdout.strip()}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Railway deployment failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    deploy_to_railway()
