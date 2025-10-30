@echo off
cls
echo ========================================
echo   PUSH TO GITHUB - SIMPLE METHOD
echo ========================================
echo.
echo Aapka code push karne ke liye:
echo.
echo 1. GitHub Desktop install karo (agar nahi hai)
echo    Download: https://desktop.github.com/
echo.
echo 2. Ya manually push karo:
echo.
echo    git push personal deploy-updates-1029-1957
echo.
echo 3. Ya browser mein repository khol ke manually upload karo:
echo    https://github.com/sanakausar356/testgenie-epicroast-new
echo.
pause
echo.
echo Trying automated push...
git push personal deploy-updates-1029-1957
echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo ✅ SUCCESS! Code pushed to GitHub!
    echo ========================================
    echo.
    echo Ab auto-deploy ke liye:
    echo 1. Railway: https://railway.app
    echo 2. Vercel: https://vercel.com
    echo 3. GitHub secrets setup karo: README_DEPLOY.md dekho
    echo.
) else (
    echo ========================================
    echo ❌ Push failed
    echo ========================================
    echo.
    echo Solutions:
    echo 1. GitHub Desktop use karo (easiest)
    echo 2. Personal Access Token banao:
    echo    https://github.com/settings/tokens
    echo 3. Network check karo
    echo.
)
pause

