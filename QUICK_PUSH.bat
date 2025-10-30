@echo off
echo Opening GitHub Desktop to push...
start "" "C:\Users\IbtasamAli\AppData\Local\GitHubDesktop\GitHubDesktop.exe" --open-in-browser "%CD%"
echo.
echo GitHub Desktop should open now.
echo Please push your changes from there!
echo.
echo After pushing, your code will auto-deploy to:
echo - Railway (Backend)
echo - Vercel (Frontend)
echo.
pause

