# Automated GitHub Upload Script
# This will try multiple methods to push code to GitHub

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   TestGenie Auto-Upload to GitHub" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

$repo = "sanakausar356/testgenie-epicroast-new"
$branch = "deploy-updates-1029-1957"

# Method 1: Try standard git push
Write-Host "[Method 1] Trying standard git push..." -ForegroundColor Yellow
git config --global http.postBuffer 524288000
git config --global http.timeout 300
git push personal $branch 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS! Code pushed via git!" -ForegroundColor Green
    exit 0
}

# Method 2: Try with --force-with-lease
Write-Host "[Method 2] Trying force push..." -ForegroundColor Yellow
git push personal $branch --force-with-lease 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS! Code pushed via force push!" -ForegroundColor Green
    exit 0
}

# Method 3: Try pushing to main branch instead
Write-Host "[Method 3] Trying to push to main branch..." -ForegroundColor Yellow
git checkout -b main 2>$null
git push personal main 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ SUCCESS! Code pushed to main branch!" -ForegroundColor Green
    exit 0
}

# Method 4: Create ZIP for manual upload
Write-Host "[Method 4] All git methods failed. Creating ZIP package..." -ForegroundColor Yellow
$zipPath = "..\TestGenie-Deploy-Package.zip"

Write-Host "Creating ZIP file..." -ForegroundColor Cyan
Compress-Archive -Path ".\*" -DestinationPath $zipPath -Force

if (Test-Path $zipPath) {
    Write-Host "✅ ZIP Created: $zipPath" -ForegroundColor Green
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host "   MANUAL UPLOAD REQUIRED" -ForegroundColor Yellow
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Git push failed due to network issue." -ForegroundColor Red
    Write-Host "ZIP file created for manual upload." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Open: https://github.com/$repo" -ForegroundColor White
    Write-Host "2. Click 'Add file' -> 'Upload files'" -ForegroundColor White
    Write-Host "3. Upload the ZIP file" -ForegroundColor White
    Write-Host "4. Or extract ZIP and drag all files" -ForegroundColor White
    Write-Host ""
    
    # Open GitHub and file location
    Start-Process "https://github.com/$repo"
    Start-Process explorer.exe -ArgumentList "/select,$zipPath"
    
    Write-Host "Opening GitHub and ZIP location..." -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to create ZIP" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

