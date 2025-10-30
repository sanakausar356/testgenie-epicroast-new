@echo off
color 0B
cls
echo.
echo  ╔════════════════════════════════════════════════╗
echo  ║   TestGenie - FINAL DEPLOYMENT SOLUTION       ║
echo  ║   Network Issue Workaround                    ║
echo  ╚════════════════════════════════════════════════╝
echo.
echo  ✅ Git Bundle Created: testgenie-complete.bundle
echo  ✅ Size: ~58 MB (all your code + history)
echo  ✅ All commits ready to deploy
echo.
echo  ════════════════════════════════════════════════
echo.
echo  🚀 DEPLOYMENT OPTIONS:
echo.
echo  [1] Open GitHub Repository (Manual Upload)
echo  [2] Try Git Push Again
echo  [3] Create ZIP File for Upload
echo  [4] Open Railway Dashboard
echo  [5] Open Vercel Dashboard
echo  [6] View Complete Instructions
echo  [0] Exit
echo.
echo  ════════════════════════════════════════════════
echo.
set /p choice="  Choose option (0-6): "

if "%choice%"=="1" goto github
if "%choice%"=="2" goto push
if "%choice%"=="3" goto zip
if "%choice%"=="4" goto railway
if "%choice%"=="5" goto vercel
if "%choice%"=="6" goto instructions
if "%choice%"=="0" goto end

:github
echo.
echo  Opening GitHub...
start https://github.com/sanakausar356/testgenie-epicroast-new
echo.
echo  ════════════════════════════════════════════════
echo  Instructions:
echo  ════════════════════════════════════════════════
echo.
echo  1. Click "Add file" → "Upload files"
echo  2. Drag ALL files from TestGenie folder
echo  3. Commit message: "Initial deployment"
echo  4. Click "Commit changes"
echo.
echo  Files to upload:
echo  - All .py files
echo  - All .bat files
echo  - All .md files
echo  - backend/ folder
echo  - frontend/ folder
echo  - .github/ folder
echo  - Everything!
echo.
pause
goto end

:push
echo.
echo  Trying to push...
echo  ════════════════════════════════════════════════
git push personal deploy-updates-1029-1957
if %errorlevel% equ 0 (
    echo.
    echo  ✅ SUCCESS! Code pushed!
) else (
    echo.
    echo  ❌ Still failing. Use Option 1 or 3.
)
echo.
pause
goto end

:zip
echo.
echo  Creating ZIP file...
echo  ════════════════════════════════════════════════
powershell -command "Compress-Archive -Path '.\*' -DestinationPath '..\TestGenie-Upload.zip' -Force"
if %errorlevel% equ 0 (
    echo.
    echo  ✅ ZIP Created: TestGenie-Upload.zip
    echo  Location: C:\Users\IbtasamAli\Downloads\TestGenie\
    echo.
    echo  Now upload this ZIP to GitHub!
    start ..\
) else (
    echo  Failed to create ZIP
)
echo.
pause
goto end

:railway
echo.
echo  Opening Railway...
start https://railway.app
echo.
echo  ════════════════════════════════════════════════
echo  Railway Deployment Steps:
echo  ════════════════════════════════════════════════
echo.
echo  1. Click "New Project"
echo  2. Select "Deploy from GitHub repo"
echo  3. Choose: sanakausar356/testgenie-epicroast-new
echo  4. Root Directory: backend
echo  5. Deploy!
echo.
pause
goto end

:vercel
echo.
echo  Opening Vercel...
start https://vercel.com
echo.
echo  ════════════════════════════════════════════════
echo  Vercel Deployment Steps:
echo  ════════════════════════════════════════════════
echo.
echo  1. Click "Add New" → "Project"
echo  2. Import: sanakausar356/testgenie-epicroast-new
echo  3. Root Directory: frontend
echo  4. Deploy!
echo.
pause
goto end

:instructions
cls
echo.
echo  ════════════════════════════════════════════════
echo  COMPLETE DEPLOYMENT GUIDE
echo  ════════════════════════════════════════════════
echo.
echo  PROBLEM: Git push failing due to network issue
echo  SOLUTION: Manual upload + Deploy
echo.
echo  ───────────────────────────────────────────────
echo  STEP 1: Upload Code to GitHub
echo  ───────────────────────────────────────────────
echo.
echo  Method A: Direct Upload (Easiest)
echo  1. Go to: github.com/sanakausar356/testgenie-epicroast-new
echo  2. Click "Add file" → "Upload files"
echo  3. Drag TestGenie folder contents
echo  4. Commit!
echo.
echo  Method B: Use ZIP
echo  1. Run Option 3 to create ZIP
echo  2. Upload ZIP to GitHub
echo.
echo  ───────────────────────────────────────────────
echo  STEP 2: Deploy Backend (Railway)
echo  ───────────────────────────────────────────────
echo.
echo  1. Visit: railway.app
echo  2. New Project → Deploy from GitHub
echo  3. Select your repo
echo  4. Root: backend
echo  5. Deploy!
echo.
echo  ───────────────────────────────────────────────
echo  STEP 3: Deploy Frontend (Vercel)
echo  ───────────────────────────────────────────────
echo.
echo  1. Visit: vercel.com
echo  2. New Project
echo  3. Import your GitHub repo
echo  4. Root: frontend
echo  5. Deploy!
echo.
echo  ───────────────────────────────────────────────
echo  AUTO-DEPLOY (Optional)
echo  ───────────────────────────────────────────────
echo.
echo  After first deploy, add GitHub secrets for auto-deploy:
echo  - RAILWAY_TOKEN
echo  - VERCEL_TOKEN
echo  - VERCEL_ORG_ID
echo  - VERCEL_PROJECT_ID
echo.
echo  Details in: SETUP_SECRETS.md
echo.
echo  ════════════════════════════════════════════════
echo.
pause
goto end

:end
exit

