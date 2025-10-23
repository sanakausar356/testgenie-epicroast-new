"""
Deploy to GitHub
"""

import subprocess
import os

def deploy_to_github():
    """Deploy code to GitHub"""
    print("🐙 Deploying to GitHub...")
    
    try:
        # Check git status
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("📝 Committing changes...")
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", "Deploy GroomRoom vNext implementation"], check=True)
        
        # Push to GitHub
        print("📤 Pushing to GitHub...")
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Successfully deployed to GitHub")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ GitHub deployment failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    deploy_to_github()
