@echo off
echo ========================================
echo  Railway Variables Setup
echo ========================================
echo.

echo Opening Railway project...
start "" "https://railway.app/dashboard"

timeout /t 2 >nul

echo.
echo ========================================
echo  COPY & PASTE THESE VARIABLES:
echo ========================================
echo.
echo 1. Go to Railway dashboard
echo 2. Find your "web" project
echo 3. Click on service -^> Variables tab
echo 4. Click "New Variable" for each:
echo.
echo Variable 1:
echo   Name: AZURE_OPENAI_ENDPOINT
echo   Value: [Your Azure endpoint]
echo.
echo Variable 2:
echo   Name: AZURE_OPENAI_API_KEY
echo   Value: [Your Azure key]
echo.
echo Variable 3:
echo   Name: AZURE_OPENAI_DEPLOYMENT_NAME
echo   Value: [Your deployment name]
echo.
echo Variable 4:
echo   Name: JIRA_BASE_URL
echo   Value: [Your Jira URL]
echo.
echo Variable 5:
echo   Name: JIRA_EMAIL
echo   Value: [Your Jira email]
echo.
echo Variable 6:
echo   Name: JIRA_API_TOKEN
echo   Value: [Your Jira token]
echo.
echo Variable 7:
echo   Name: PORT
echo   Value: 8000
echo.
echo ========================================
echo  AFTER ADDING VARIABLES:
echo ========================================
echo.
echo Railway will auto-redeploy (1-2 min)
echo Then test: https://frontend-a217e8xvj-sana-ks-projects.vercel.app
echo.
echo ========================================
pause

