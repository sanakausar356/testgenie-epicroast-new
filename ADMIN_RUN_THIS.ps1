# Admin: Run this PowerShell script to deploy Ibtasam's changes to production
# Usage: .\ADMIN_RUN_THIS.ps1

Write-Host "`n🚀 Deploying TestGenie Updates to Production" -ForegroundColor Cyan
Write-Host "==============================================`n" -ForegroundColor Cyan

# ADMIN: Update this path to your local repository path
$repoPath = "C:\path\to\summervibe-testgenie-epicroast"

# Navigate to repository
Write-Host "📍 Step 1: Navigate to repository..." -ForegroundColor Yellow
if (Test-Path $repoPath) {
    Set-Location $repoPath
    Write-Host "✅ Current directory: $(Get-Location)`n" -ForegroundColor Green
} else {
    Write-Host "❌ Error: Repository path not found: $repoPath" -ForegroundColor Red
    Write-Host "Please update the `$repoPath variable at the top of this script.`n" -ForegroundColor Yellow
    exit 1
}

# Check if remote already exists
Write-Host "📍 Step 2: Add Ibtasam's repository..." -ForegroundColor Yellow
$remotes = git remote
if ($remotes -contains "ibtasam") {
    Write-Host "✅ Remote 'ibtasam' already exists`n" -ForegroundColor Green
} else {
    git remote add ibtasam https://github.com/Ibtasamali01/TestGenie.git
    Write-Host "✅ Added remote 'ibtasam'`n" -ForegroundColor Green
}

# Fetch latest changes
Write-Host "📍 Step 3: Fetch latest changes from Ibtasam..." -ForegroundColor Yellow
git fetch ibtasam
Write-Host "✅ Fetched successfully`n" -ForegroundColor Green

# Show what will be merged
Write-Host "📍 Step 4: Preview changes..." -ForegroundColor Yellow
Write-Host "Commits to be merged:" -ForegroundColor Cyan
git log HEAD..ibtasam/main --oneline | Select-Object -First 20
Write-Host ""

# Ask for confirmation
$confirmation = Read-Host "Do you want to merge these changes? (yes/no)"
if ($confirmation -ne "yes") {
    Write-Host "`n❌ Deployment cancelled by user." -ForegroundColor Red
    exit 0
}

# Merge changes
Write-Host "`n📍 Step 5: Merging changes..." -ForegroundColor Yellow
git merge ibtasam/main -m "Merge latest updates from Ibtasam: Enhanced AC suggestions, Jira status integration, bug fixes"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Merge successful!`n" -ForegroundColor Green
    
    # Push to origin
    Write-Host "📍 Step 6: Pushing to origin (triggers Vercel deployment)..." -ForegroundColor Yellow
    git push origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n🎉 SUCCESS! Deployment initiated!`n" -ForegroundColor Green
        Write-Host "✅ Changes pushed to GitHub" -ForegroundColor Green
        Write-Host "✅ Vercel will auto-deploy in 2-3 minutes" -ForegroundColor Green
        Write-Host "🔗 URL: https://summervibe-testgenie-epicroast.vercel.app/`n" -ForegroundColor Cyan
        
        Write-Host "Changes deployed:" -ForegroundColor Yellow
        Write-Host "  ✅ Enhanced AC suggestions (8-12 clauses, professional)" -ForegroundColor Green
        Write-Host "  ✅ Jira status integration" -ForegroundColor Green
        Write-Host "  ✅ Cleaner output formatting" -ForegroundColor Green
        Write-Host "  ✅ Bug fixes and improvements`n" -ForegroundColor Green
    } else {
        Write-Host "`n❌ Error pushing to origin. Check permissions.`n" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n❌ Merge failed. Resolve conflicts manually:" -ForegroundColor Red
    Write-Host "   git status" -ForegroundColor Yellow
    Write-Host "   # Fix conflicts in files" -ForegroundColor Yellow
    Write-Host "   git add ." -ForegroundColor Yellow
    Write-Host "   git commit" -ForegroundColor Yellow
    Write-Host "   git push origin main`n" -ForegroundColor Yellow
    exit 1
}

