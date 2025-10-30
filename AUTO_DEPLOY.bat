@echo off
echo ========================================
echo TestGenie Auto-Deploy Script
echo ========================================
echo.

REM Add all changes
echo [1/4] Adding all changes...
git add .

REM Commit changes
echo [2/4] Committing changes...
set /p COMMIT_MSG="Enter commit message (or press Enter for default): "
if "%COMMIT_MSG%"=="" set COMMIT_MSG="Auto-deploy: Update code"
git commit -m "%COMMIT_MSG%"

REM Push to GitHub
echo [3/4] Pushing to GitHub...
git push personal deploy-updates-1029-1957

if %errorlevel% neq 0 (
    echo.
    echo Trying alternative push method...
    git push personal HEAD:main
)

REM Trigger deploys
echo [4/4] Deployments will auto-trigger via GitHub Actions...

echo.
echo ========================================
echo ✅ Code pushed! 
echo.
echo Auto-deploy will happen automatically:
echo - Railway: Backend will deploy
echo - Vercel: Frontend will deploy
echo.
echo Check deployment status:
echo - Railway: https://railway.app
echo - Vercel: https://vercel.com/dashboard
echo ========================================
pause

