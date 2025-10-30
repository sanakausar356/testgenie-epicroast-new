@echo off
echo ========================================
echo TestGenie - Move to New Repository
echo ========================================
echo.

REM Get new repository URL from user
set /p NEW_REPO_URL="Enter your new GitHub repository URL (e.g., https://github.com/username/repo.git): "

if "%NEW_REPO_URL%"=="" (
    echo ERROR: Repository URL cannot be empty!
    pause
    exit /b 1
)

echo.
echo Step 1: Adding new remote 'origin'...
git remote add origin %NEW_REPO_URL%

if %errorlevel% neq 0 (
    echo.
    echo Remote 'origin' might already exist. Updating it...
    git remote set-url origin %NEW_REPO_URL%
)

echo.
echo Step 2: Checking remotes...
git remote -v

echo.
echo Step 3: Adding all files...
git add .

echo.
echo Step 4: Committing changes...
git commit -m "Move to new repository"

if %errorlevel% equ 0 (
    echo Commit successful!
) else (
    echo No changes to commit or commit failed
)

echo.
echo Step 5: Pushing to new repository...
echo Current branch: deploy-updates-1029-1957
echo.
choice /C YN /M "Do you want to push to 'main' branch instead of 'deploy-updates-1029-1957'"

if errorlevel 2 goto push_current
if errorlevel 1 goto push_main

:push_main
echo.
echo Creating and switching to 'main' branch...
git checkout -b main
git push -u origin main
goto end

:push_current
echo.
echo Pushing current branch...
git push -u origin deploy-updates-1029-1957
goto end

:end
echo.
echo ========================================
echo.
if %errorlevel% equ 0 (
    echo SUCCESS! Your code has been pushed to the new repository!
    echo Repository URL: %NEW_REPO_URL%
) else (
    echo FAILED! There was an error pushing to the repository.
    echo Please check the error messages above.
)
echo.
echo ========================================
pause

