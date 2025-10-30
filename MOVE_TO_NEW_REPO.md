# Move TestGenie to New Repository

## Quick Steps:

### 1. Create New GitHub Repository
Go to GitHub and create a new **empty** repository (don't add README, .gitignore, or LICENSE)

### 2. Run These Commands:

```powershell
# Make sure you're in the TestGenie directory
cd C:\Users\IbtasamAli\Downloads\TestGenie\TestGenie

# Add your new repository as remote (replace YOUR_USERNAME and YOUR_REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Check all remotes
git remote -v

# Add all untracked files
git add .

# Commit any remaining changes
git commit -m "Initial commit for new repository"

# Push to new repository
git push -u origin deploy-updates-1029-1957

# Or if you want to push to main branch:
git checkout -b main
git push -u origin main
```

### 3. (Optional) Remove Old Remotes:

```powershell
# Remove old remotes if you don't need them
git remote remove admin-origin
git remote remove personal
```

## Alternative: Fresh Start with All History

If you want to push all branches:

```powershell
# Push all branches
git push origin --all

# Push all tags
git push origin --tags
```

## Alternative: Start Fresh Repository (Clean History)

If you want to start fresh without old history:

```powershell
# Remove old .git folder (CAREFUL - this removes all git history!)
Remove-Item -Recurse -Force .git

# Initialize new git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit"

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Create and push to main branch
git branch -M main
git push -u origin main
```

## Current Repository Info:

- **Current Branch:** deploy-updates-1029-1957
- **Existing Remotes:**
  - admin-origin: NewellBrands/summervibe-testgenie-epicroast
  - personal: sanakausar356/testgenie-epicroast-new

- **Recent Commits:**
  - 6ddc9fe - add: Railway and GitHub push automation scripts
  - 77d8a2c - fix: Update Vercel config for frontend folder
  - 2f3046b - fix: Update Vercel and Railway config
  - 74c2409 - trigger deploy
  - b330a08 - fix: Remove proxy settings to fix Azure OpenAI initialization

Choose the approach that best fits your needs!

