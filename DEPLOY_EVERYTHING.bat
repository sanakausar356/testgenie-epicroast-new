@echo off
color 0A
cls
echo.
echo  ╔═══════════════════════════════════════╗
echo  ║   TestGenie Auto-Deploy System       ║
echo  ║   Git + Railway + Vercel             ║
echo  ╚═══════════════════════════════════════╝
echo.
echo  Current Repository:
echo  https://github.com/sanakausar356/testgenie-epicroast-new
echo.
echo  ─────────────────────────────────────────
echo.
echo  [1] Push to GitHub (Try Now)
echo  [2] Open GitHub in Browser
echo  [3] Open Railway Dashboard
echo  [4] Open Vercel Dashboard
echo  [5] View Setup Instructions
echo  [6] Exit
echo.
echo  ─────────────────────────────────────────
echo.
set /p choice="  Select option (1-6): "

if "%choice%"=="1" goto push
if "%choice%"=="2" goto github
if "%choice%"=="3" goto railway
if "%choice%"=="4" goto vercel
if "%choice%"=="5" goto instructions
if "%choice%"=="6" goto end

:push
cls
echo.
echo  Pushing to GitHub...
echo  ───────────────────────────────────────────
echo.
git add .
git commit -m "Deploy update - %date% %time%"
git push personal deploy-updates-1029-1957
echo.
if %errorlevel% equ 0 (
    color 0A
    echo  ✅ SUCCESS! Code pushed to GitHub!
    echo.
    echo  Your code is now at:
    echo  https://github.com/sanakausar356/testgenie-epicroast-new
    echo.
    echo  Next: Deploy on Railway and Vercel
) else (
    color 0C
    echo  ❌ Push failed!
    echo.
    echo  Solutions:
    echo  1. Use GitHub Desktop (easiest)
    echo  2. Check internet connection
    echo  3. Try manual upload to GitHub
)
echo.
pause
goto end

:github
start https://github.com/sanakausar356/testgenie-epicroast-new
echo  Opening GitHub...
timeout /t 2 >nul
goto end

:railway
start https://railway.app
echo  Opening Railway...
timeout /t 2 >nul
goto end

:vercel
start https://vercel.com/dashboard
echo  Opening Vercel...
timeout /t 2 >nul
goto end

:instructions
cls
echo.
echo  ╔═══════════════════════════════════════════════════════╗
echo  ║          DEPLOYMENT INSTRUCTIONS                     ║
echo  ╚═══════════════════════════════════════════════════════╝
echo.
echo  📁 Files Ready:
echo  ✅ .github/workflows/deploy.yml (Auto-deploy)
echo  ✅ railway.json (Railway config)
echo  ✅ vercel.json (Vercel config)
echo  ✅ All necessary scripts
echo.
echo  🚀 Quick Deploy:
echo.
echo  1. PUSH TO GITHUB:
echo     git push personal deploy-updates-1029-1957
echo.
echo  2. DEPLOY RAILWAY (Backend):
echo     - Go to: https://railway.app
echo     - New Project → Deploy from GitHub
echo     - Select: sanakausar356/testgenie-epicroast-new
echo     - Root: backend
echo.
echo  3. DEPLOY VERCEL (Frontend):
echo     - Go to: https://vercel.com
echo     - Add New → Project
echo     - Import: sanakausar356/testgenie-epicroast-new
echo     - Root: frontend
echo.
echo  📚 For details, read: START_HERE.md
echo.
pause
goto end

:end
exit

