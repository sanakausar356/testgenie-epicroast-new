@echo off
echo ========================================
echo  Pushing to GitHub - Please Login
echo ========================================
echo.

cd /d "%~dp0"

echo Opening GitHub Desktop...
start "" "https://desktop.github.com/"

echo.
echo INSTRUCTIONS:
echo 1. GitHub Desktop will open
echo 2. Sign in if needed
echo 3. File -^> Add Local Repository
echo 4. Choose: %CD%
echo 5. You'll see 4-5 files changed
echo 6. Click "Commit to deploy-updates-1029-1957"
echo 7. Click "Publish branch" or "Push origin"
echo.
echo After push, Railway will auto-deploy!
echo.
pause

echo.
echo Checking if GitHub Desktop pushed...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo  NEXT: Configure Railway
echo ========================================
echo.
echo Go to: https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47
echo.
echo Settings -^> Source:
echo   Repo: sanakausar356/testgenie-epicroast-new
echo   Branch: main
echo.
echo Then click "Deploy"
echo ========================================
pause

