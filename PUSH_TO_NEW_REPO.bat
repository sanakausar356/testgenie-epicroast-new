@echo off
echo Pushing to new repository...
git push personal deploy-updates-1029-1957
if %errorlevel% neq 0 (
    echo.
    echo Failed with HTTPS. Trying to push all branches...
    git push personal --all
)
pause

