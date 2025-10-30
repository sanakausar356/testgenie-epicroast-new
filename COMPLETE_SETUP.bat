@echo off
cls
echo ========================================
echo   TestGenie Complete Setup
echo   Git + Vercel + Railway Auto-Deploy
echo ========================================
echo.
echo This will:
echo 1. Connect to your new GitHub repo
echo 2. Setup Vercel deployment
echo 3. Setup Railway deployment
echo 4. Push all code
echo.
pause

REM Step 1: Check Git remote
echo.
echo [Step 1/5] Checking Git configuration...
git remote -v
echo.

REM Step 2: Try to push to GitHub
echo [Step 2/5] Pushing to GitHub (sanakausar356/testgenie-epicroast-new)...
git push -u personal deploy-updates-1029-1957 2>push_error.txt

if %errorlevel% neq 0 (
    echo Push failed with HTTPS. Let's try SSH...
    echo.
    echo Please run these commands manually:
    echo.
    echo git remote set-url personal git@github.com:sanakausar356/testgenie-epicroast-new.git
    echo git push -u personal deploy-updates-1029-1957
    echo.
    echo OR open GitHub Desktop and push from there.
    echo.
    pause
    exit /b 1
)

REM Step 3: Setup Vercel
echo.
echo [Step 3/5] Setting up Vercel...
cd frontend
call npm install -g vercel 2>nul
call vercel --version
if %errorlevel% equ 0 (
    echo Vercel CLI found! You can deploy with: vercel --prod
) else (
    echo Install Vercel CLI: npm install -g vercel
)
cd ..

REM Step 4: Setup Railway
echo.
echo [Step 4/5] Setting up Railway...
call npm install -g @railway/cli 2>nul
call railway --version
if %errorlevel% equ 0 (
    echo Railway CLI found! You can deploy with: railway up
) else (
    echo Install Railway CLI: npm install -g @railway/cli
)

REM Step 5: Instructions
echo.
echo [Step 5/5] Next Steps...
echo.
echo ========================================
echo ✅ Setup Complete!
echo ========================================
echo.
echo To enable AUTO-DEPLOY:
echo 1. Go to: https://github.com/sanakausar356/testgenie-epicroast-new/settings/secrets/actions
echo 2. Add these secrets:
echo    - RAILWAY_TOKEN (from https://railway.app/account/tokens)
echo    - VERCEL_TOKEN (from https://vercel.com/account/tokens)
echo    - VERCEL_ORG_ID
echo    - VERCEL_PROJECT_ID
echo.
echo Then just run AUTO_DEPLOY.bat to deploy!
echo.
echo OR manually deploy:
echo - Railway: cd backend ^&^& railway up
echo - Vercel: cd frontend ^&^& vercel --prod
echo.
echo ========================================
pause

