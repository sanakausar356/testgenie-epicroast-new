@echo off
echo ========================================
echo  Railway Auto-Setup
echo ========================================
echo.

echo Opening Railway project settings...
start "" "https://railway.com/project/72d8fa1a-05e0-47e4-a9eb-c88021c8dd47"

echo.
echo INSTRUCTIONS:
echo.
echo 1. Click on your SERVICE (backend)
echo 2. Go to SETTINGS tab
echo.
echo 3. SOURCE section:
echo    Click EDIT or pencil icon
echo    Repository: sanakausar356/testgenie-epicroast-new
echo    Branch: main
echo    Click SAVE
echo.
echo 4. ENVIRONMENT VARIABLES:
echo    Add these (if not already added):
echo    - AZURE_OPENAI_ENDPOINT
echo    - AZURE_OPENAI_API_KEY
echo    - AZURE_OPENAI_DEPLOYMENT_NAME
echo    - JIRA_BASE_URL
echo    - JIRA_EMAIL
echo    - JIRA_API_TOKEN
echo    - PORT=8000
echo.
echo 5. Click DEPLOY button (top right)
echo.
echo 6. Wait 3-5 minutes for deployment
echo.
echo ========================================
echo  Your URLs:
echo  Frontend: https://frontend-2d8snuuof-sana-ks-projects.vercel.app
echo  Backend: https://web-production-8415f.up.railway.app
echo ========================================
echo.
pause

