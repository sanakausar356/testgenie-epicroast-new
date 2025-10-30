@echo off
echo ========================================
echo TestGenie - Fresh Start New Repository
echo (This will REMOVE all Git history!)
echo ========================================
echo.

echo WARNING: This will delete all existing Git history!
echo.
choice /C YN /M "Are you sure you want to continue"

if errorlevel 2 goto cancel
if errorlevel 1 goto continue

:cancel
echo Operation cancelled.
pause
exit /b 0

:continue
REM Get new repository URL from user
set /p NEW_REPO_URL="Enter your new GitHub repository URL (e.g., https://github.com/username/repo.git): "

if "%NEW_REPO_URL%"=="" (
    echo ERROR: Repository URL cannot be empty!
    pause
    exit /b 1
)

echo.
echo Step 1: Removing old .git folder...
if exist .git (
    rmdir /s /q .git
    echo Old Git history removed!
) else (
    echo No .git folder found
)

echo.
echo Step 2: Initializing new Git repository...
git init

echo.
echo Step 3: Adding all files...
git add .

echo.
echo Step 4: Creating initial commit...
git commit -m "Initial commit - Fresh start"

echo.
echo Step 5: Creating main branch...
git branch -M main

echo.
echo Step 6: Adding remote origin...
git remote add origin %NEW_REPO_URL%

echo.
echo Step 7: Pushing to new repository...
git push -u origin main

echo.
echo ========================================
echo.
if %errorlevel% equ 0 (
    echo SUCCESS! Fresh repository created and pushed!
    echo Repository URL: %NEW_REPO_URL%
) else (
    echo FAILED! There was an error.
    echo Please check the error messages above.
)
echo.
echo ========================================
pause

