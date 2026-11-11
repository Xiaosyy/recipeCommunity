@echo off
:: RecipeShare Local Custom Domain Setup
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting Administrator privileges to update hosts file...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

set HOSTS=%WINDIR%\System32\drivers\etc\hosts

findstr /i "recipeshare.local" "%HOSTS%" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] recipeshare.local is already configured in Windows hosts.
) else (
    echo. >> "%HOSTS%"
    echo 127.0.0.1 recipeshare.local >> "%HOSTS%"
    echo 127.0.0.1 www.recipeshare.local >> "%HOSTS%"
    echo [OK] Added recipeshare.local to %HOSTS%
)

ipconfig /flushdns >nul

echo.
echo ========================================================
echo  Success! Your custom URL is ready:
echo  http://recipeshare.local:5000
echo ========================================================
echo.
pause

