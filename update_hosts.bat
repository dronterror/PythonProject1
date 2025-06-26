@echo off
echo Adding hosts entries for ValMed Keycloak setup...
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Right-click on this file and select "Run as administrator"
    pause
    exit /b 1
)

REM Add the hosts entries
echo 127.0.0.1 medlog.local api.medlog.local keycloak.medlog.local >> C:\Windows\System32\drivers\etc\hosts

echo.
echo Hosts entries added successfully!
echo.
echo Added:
echo   127.0.0.1 medlog.local api.medlog.local keycloak.medlog.local
echo.
echo You can now access:
echo   - Frontend: http://medlog.local
echo   - Backend API: http://api.medlog.local
echo   - Keycloak Admin: http://keycloak.medlog.local
echo.
pause 