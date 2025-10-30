@echo off
echo ========================================
echo TestGenie Manual Deploy Script
echo ========================================
echo.

REM Check if Railway CLI is installed
where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo Railway CLI not found. Installing...
    npm install -g @railway/cli
)

REM Check if Vercel CLI is installed
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo Vercel CLI not found. Installing...
    npm install -g vercel
)

echo.
echo [1/4] Adding and committing changes...
git add .
git commit -m "Manual deploy update"

echo.
echo [2/4] Pushing to GitHub...
git push personal deploy-updates-1029-1957
if %errorlevel% neq 0 (
    git push personal HEAD:main
)

echo.
echo [3/4] Deploying to Railway...
cd backend
railway up
cd ..

echo.
echo [4/4] Deploying to Vercel...
cd frontend
vercel --prod
cd ..

echo.
echo ========================================
echo ✅ Deployment Complete!
echo ========================================
pause

