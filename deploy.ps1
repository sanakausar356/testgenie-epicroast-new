# TestGenie Deployment Script for PowerShell
# This script helps you push your code to GitHub

Write-Host "🚀 TestGenie Deployment Helper" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✅ Git is installed: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Git is not installed. Please install Git first." -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 1: Initializing Git repository..." -ForegroundColor Yellow

# Initialize git if not already done
if (-not (Test-Path ".git")) {
    git init
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 2: Adding all files..." -ForegroundColor Yellow
git add .
Write-Host "✅ Files added" -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Creating commit..." -ForegroundColor Yellow
$commitMessage = "Initial commit - TestGenie deployment ready"
git commit -m $commitMessage
Write-Host "✅ Commit created" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📝 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create a GitHub repository:" -ForegroundColor White
Write-Host "   → Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "   → Name: TestGenie" -ForegroundColor Cyan
Write-Host "   → DO NOT initialize with README" -ForegroundColor Red
Write-Host ""
Write-Host "2. After creating the repository, run these commands:" -ForegroundColor White
Write-Host "   (Replace YOUR_USERNAME with your GitHub username)" -ForegroundColor Yellow
Write-Host ""
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/TestGenie.git" -ForegroundColor Cyan
Write-Host "   git branch -M main" -ForegroundColor Cyan
Write-Host "   git push -u origin main" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Then follow the deployment guide:" -ForegroundColor White
Write-Host "   → Read: QUICK_DEPLOY_STEPS.md" -ForegroundColor Cyan
Write-Host "   → Or: DEPLOYMENT_INSTRUCTIONS.md (detailed guide)" -ForegroundColor Cyan
Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Prompt to continue
Write-Host "Would you like to add the GitHub remote now? (y/n): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq 'y' -or $response -eq 'Y') {
    Write-Host ""
    Write-Host "Enter your GitHub username: " -ForegroundColor Yellow -NoNewline
    $username = Read-Host
    
    $repoUrl = "https://github.com/$username/TestGenie.git"
    
    Write-Host ""
    Write-Host "Adding remote: $repoUrl" -ForegroundColor Cyan
    
    try {
        git remote add origin $repoUrl
        git branch -M main
        Write-Host "✅ Remote added successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Now you can push to GitHub by running:" -ForegroundColor Yellow
        Write-Host "   git push -u origin main" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Would you like to push now? (y/n): " -ForegroundColor Yellow -NoNewline
        $pushResponse = Read-Host
        
        if ($pushResponse -eq 'y' -or $pushResponse -eq 'Y') {
            Write-Host ""
            Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
            git push -u origin main
            Write-Host ""
            Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
            Write-Host ""
            Write-Host "Next: Deploy to Railway and Vercel" -ForegroundColor Yellow
            Write-Host "Read: QUICK_DEPLOY_STEPS.md (Steps 2 and 3)" -ForegroundColor Cyan
        }
    } catch {
        Write-Host "❌ Error adding remote. Please add it manually." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Git setup complete!" -ForegroundColor Green
Write-Host ""

