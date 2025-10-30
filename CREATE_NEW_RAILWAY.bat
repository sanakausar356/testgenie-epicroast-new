@echo off
echo ========================================
echo  Create NEW Railway Project (Fresh Start!)
echo ========================================
echo.

echo Opening Railway Dashboard...
start "" "https://railway.app/new"

timeout /t 2 >nul

echo.
echo ========================================
echo  FOLLOW THESE STEPS:
echo ========================================
echo.
echo Step 1: Click "Deploy from GitHub repo"
echo.
echo Step 2: Select Repository:
echo   - sanakausar356/testgenie-epicroast-new
echo   - (If not visible, click "Configure GitHub App")
echo.
echo Step 3: Railway will ask which folder:
echo   - Root Directory: / (leave empty)
echo   - Or: backend (if it asks)
echo.
echo Step 4: Add Environment Variables:
echo   Click "Variables" and add:
echo.
echo   AZURE_OPENAI_ENDPOINT=your-endpoint
echo   AZURE_OPENAI_API_KEY=your-key
echo   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
echo   JIRA_BASE_URL=your-jira-url
echo   JIRA_EMAIL=your-email  
echo   JIRA_API_TOKEN=your-token
echo   PORT=8000
echo.
echo Step 5: Click "Deploy"
echo.
echo Step 6: Wait 3-5 minutes
echo.
echo Step 7: Copy the Railway URL (like: https://xxx.railway.app)
echo.
echo ========================================
echo  AFTER DEPLOYMENT:
echo ========================================
echo.
echo 1. Copy your new Railway URL
echo 2. Update Vercel environment variable:
echo    Go to: https://vercel.com/sana-ks-projects/frontend/settings/environment-variables
echo    Update VITE_API_URL to your new Railway URL
echo 3. Redeploy Vercel
echo.
echo ========================================
pause

