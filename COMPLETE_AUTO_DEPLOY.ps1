# Complete Automated Deployment Script
# This script will do EVERYTHING automatically

param(
    [string]$GithubToken = ""
)

$ErrorActionPreference = "Continue"

# Colors
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Clear-Host
Write-Info "════════════════════════════════════════════════"
Write-Info "   COMPLETE AUTOMATED DEPLOYMENT"
Write-Info "   TestGenie → GitHub → Railway → Vercel"
Write-Info "════════════════════════════════════════════════"
Write-Host ""

# Step 1: Git Configuration
Write-Info "[Step 1/8] Optimizing Git configuration..."
git config --global http.postBuffer 524288000
git config --global http.timeout 300
git config --global --unset http.proxy 2>$null
git config --global --unset https.proxy 2>$null
Write-Success "✅ Git configured"
Write-Host ""

# Step 2: Commit any remaining changes
Write-Info "[Step 2/8] Checking for uncommitted changes..."
$status = git status --porcelain
if ($status) {
    git add -A
    git commit -m "Auto-deploy: Complete deployment $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
    Write-Success "✅ Changes committed"
} else {
    Write-Info "No new changes to commit"
}
Write-Host ""

# Step 3: Try to push to GitHub
Write-Info "[Step 3/8] Attempting to push to GitHub..."
$pushAttempts = @(
    @{Branch = "deploy-updates-1029-1957"; Remote = "personal"},
    @{Branch = "main"; Remote = "personal"},
    @{Branch = "deploy-updates-1029-1957"; Remote = "origin"}
)

$pushSuccess = $false
foreach ($attempt in $pushAttempts) {
    Write-Info "Trying: $($attempt.Remote)/$($attempt.Branch)..."
    git push $attempt.Remote $attempt.Branch 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "✅ Successfully pushed to $($attempt.Remote)/$($attempt.Branch)!"
        $pushSuccess = $true
        break
    }
}

if (-not $pushSuccess) {
    Write-Warning "⚠️ Git push failed (network issue)"
    Write-Info "Creating ZIP package for manual upload..."
    
    $zipPath = "..\TestGenie-Complete-Package.zip"
    Compress-Archive -Path ".\*" -DestinationPath $zipPath -Force -ErrorAction SilentlyContinue
    
    if (Test-Path $zipPath) {
        Write-Success "✅ ZIP created: $zipPath"
        Write-Warning "📦 You'll need to manually upload this ZIP to GitHub"
    }
}
Write-Host ""

# Step 4: Open GitHub
Write-Info "[Step 4/8] Opening GitHub repository..."
Start-Process "https://github.com/sanakausar356/testgenie-epicroast-new"
Start-Sleep -Seconds 2
Write-Success "✅ GitHub opened"
Write-Host ""

# Step 5: Check if Railway CLI is available
Write-Info "[Step 5/8] Checking Railway CLI..."
$railwayInstalled = $false
try {
    $railwayVersion = railway --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $railwayInstalled = $true
        Write-Success "✅ Railway CLI found"
    }
} catch {
    Write-Warning "⚠️ Railway CLI not installed"
}

if (-not $railwayInstalled) {
    Write-Info "Opening Railway dashboard for manual deployment..."
    Start-Process "https://railway.app/new"
} else {
    Write-Info "Railway CLI available - you can run 'railway up' in backend folder"
}
Write-Host ""

# Step 6: Check if Vercel CLI is available
Write-Info "[Step 6/8] Checking Vercel CLI..."
$vercelInstalled = $false
try {
    $vercelVersion = vercel --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        $vercelInstalled = $true
        Write-Success "✅ Vercel CLI found"
    }
} catch {
    Write-Warning "⚠️ Vercel CLI not installed"
}

if (-not $vercelInstalled) {
    Write-Info "Opening Vercel dashboard for manual deployment..."
    Start-Process "https://vercel.com/new"
} else {
    Write-Info "Vercel CLI available - you can run 'vercel --prod' in frontend folder"
}
Write-Host ""

# Step 7: Open documentation
Write-Info "[Step 7/8] Opening deployment documentation..."
Start-Process notepad "DEPLOYMENT_COMPLETE.md"
Write-Success "✅ Documentation opened"
Write-Host ""

# Step 8: Summary
Write-Info "[Step 8/8] Deployment Summary"
Write-Info "════════════════════════════════════════════════"
Write-Host ""

if ($pushSuccess) {
    Write-Success "✅ Code pushed to GitHub successfully!"
} else {
    Write-Warning "⚠️ Manual GitHub upload required"
    Write-Info "   Upload ZIP: TestGenie-Complete-Package.zip"
    Write-Info "   Or use: git push personal deploy-updates-1029-1957"
}

Write-Host ""
Write-Info "Next steps to complete deployment:"
Write-Host ""
Write-Info "1. GitHub (if needed):"
Write-Host "   • Verify code is uploaded"
Write-Host "   • URL: https://github.com/sanakausar356/testgenie-epicroast-new"
Write-Host ""
Write-Info "2. Railway (Backend):"
Write-Host "   • New Project → Deploy from GitHub"
Write-Host "   • Repo: sanakausar356/testgenie-epicroast-new"
Write-Host "   • Root directory: backend"
Write-Host "   • Add environment variables (AZURE_OPENAI_KEY, etc.)"
Write-Host ""
Write-Info "3. Vercel (Frontend):"
Write-Host "   • New Project → Import from GitHub"
Write-Host "   • Repo: sanakausar356/testgenie-epicroast-new"
Write-Host "   • Root directory: frontend"
Write-Host "   • Framework: Vite (auto-detect)"
Write-Host ""
Write-Success "════════════════════════════════════════════════"
Write-Success "   AUTOMATION COMPLETE!"
Write-Success "════════════════════════════════════════════════"
Write-Host ""
Write-Host "All necessary pages have been opened in your browser."
Write-Host "Follow the steps above to complete the deployment."
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

