@echo off
setlocal
echo ========================================================
echo         RecipeShare - Deploy to GitHub
echo ========================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g. https://github.com/username/repository.git): "
if "%REPO_URL%"=="" (
    echo [ERROR] No repository URL provided.
    pause
    exit /b
)

echo.
echo Connecting to GitHub repository...
tools\git\cmd\git.exe remote remove origin 2>nul
tools\git\cmd\git.exe remote add origin %REPO_URL%

echo.
echo Pushing main branch to GitHub...
tools\git\cmd\git.exe push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================================
    echo  SUCCESS: Your repository has been deployed to GitHub!
    echo ========================================================
) else (
    echo.
    echo If GitHub authentication failed:
    echo 1. Verify you have created an empty repository on GitHub.
    echo 2. When prompted for password, enter a GitHub Personal Access Token (PAT).
)
echo.
pause
