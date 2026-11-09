@echo off
rem Resets the lab user's OneDrive (Cowork task folders and the Trey Research agreement) through Microsoft Graph.
rem Optional: pass the lab username to skip the account picker, for example: reset-lab.bat user@tenant.onmicrosoft.com
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0reset-lab.ps1" -UserName "%~1"
exit /b %errorlevel%
