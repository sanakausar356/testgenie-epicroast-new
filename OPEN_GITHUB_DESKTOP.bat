@echo off
echo ========================================
echo Opening GitHub Desktop
echo ========================================
echo.

start "" "C:\Users\%USERNAME%\AppData\Local\GitHubDesktop\GitHubDesktop.exe"

timeout /t 2 >nul

echo.
echo SIMPLE STEPS IN GITHUB DESKTOP:
echo.
echo 1. If not added: File -^> Add Local Repository
echo    Path: %CD%
echo.
echo 2. Repository Settings (Ctrl+,):
echo    URL: https://github.com/sanakausar356/testgenie-epicroast-new.git
echo.
echo 3. See changes (6-7 files)
echo.
echo 4. Commit message: "fix: Proxy and Vercel config"
echo.
echo 5. Click "Push origin"
echo.
echo 6. Railway will auto-deploy in 3-5 minutes!
echo.
echo ========================================
pause

