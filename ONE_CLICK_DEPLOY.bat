@echo off
color 0B
cls
echo.
echo  ╔════════════════════════════════════════════════╗
echo  ║   ONE-CLICK COMPLETE DEPLOYMENT               ║
echo  ║   Automated Git + Railway + Vercel            ║
echo  ╚════════════════════════════════════════════════╝
echo.
echo  This will automatically:
echo  1. Try to push code to GitHub
echo  2. Create ZIP if push fails
echo  3. Open GitHub for upload
echo  4. Open Railway for backend deploy
echo  5. Open Vercel for frontend deploy
echo.
echo  ════════════════════════════════════════════════
echo.
pause

echo.
echo [1/5] Attempting to push to GitHub...
echo ════════════════════════════════════════════════
powershell -ExecutionPolicy Bypass -File "AUTO_UPLOAD_TO_GITHUB.ps1"

echo.
echo [2/5] Opening Railway for backend deployment...
echo ════════════════════════════════════════════════
timeout /t 2 >nul
start https://railway.app/new

echo.
echo [3/5] Opening Vercel for frontend deployment...
echo ════════════════════════════════════════════════
timeout /t 2 >nul
start https://vercel.com/new

echo.
echo [4/5] Opening deployment documentation...
echo ════════════════════════════════════════════════
timeout /t 1 >nul
start notepad DEPLOYMENT_COMPLETE.md

echo.
echo [5/5] Complete!
echo ════════════════════════════════════════════════
echo.
echo ✅ All deployment pages opened!
echo.
echo Next steps:
echo ───────────────────────────────────────────────
echo.
echo 1. GitHub: Upload files if git push failed
echo 2. Railway: Deploy from GitHub repo
echo    - Repo: sanakausar356/testgenie-epicroast-new
echo    - Root: backend
echo.
echo 3. Vercel: Deploy from GitHub repo
echo    - Repo: sanakausar356/testgenie-epicroast-new
echo    - Root: frontend
echo.
echo ════════════════════════════════════════════════
echo.
pause

