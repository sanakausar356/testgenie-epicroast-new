@echo off
echo ========================================
echo  Auto-Deploy Script for Vercel + Railway
echo ========================================
echo.

cd /d "%~dp0"

echo [1/4] Adding changes to git...
git add -A

echo [2/4] Committing changes...
git commit -m "fix: Update Vercel config and Railway backend URL"

echo [3/4] Pushing to GitHub (personal repo)...
git remote add origin-personal https://github.com/sanakausar356/testgenie-epicroast-new.git 2>nul
git push origin-personal deploy-updates-1029-1957:main --force

echo.
echo ========================================
echo  Done! Check deployments:
echo  Vercel: https://vercel.com/sanakausar356/testgenie-epicroast-new
echo  Railway: https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47
echo ========================================
echo.
pause

