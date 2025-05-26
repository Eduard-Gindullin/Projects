@echo off
REM Script for importing group policy settings to disable BitLocker

echo Creating GPO for BitLocker Disable Script...

REM Create new group policy
powershell.exe -Command "New-GPO -Name 'BitLocker Disable Script' -Comment 'Automatically disables BitLocker on startup'"

REM Check if script exists
if not exist "\\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-EN.ps1" (
    echo Error: Script not found at \\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-EN.ps1
    echo Please ensure the script is in place before running this GPO setup
    pause
    exit /b 1
)

REM Check and create log directory if it doesn't exist
if not exist "\\SP63210003\Dist\Bitlocker\BitlockerLog" mkdir "\\SP63210003\Dist\Bitlocker\BitlockerLog"

REM Configure PowerShell script execution through group policy
powershell.exe -Command "$gpo = Get-GPO -Name 'BitLocker Disable Script'; Set-GPPrefRegistryValue -Name $gpo.DisplayName -Context Computer -Action Create -Key 'HKLM\Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Startup\0' -ValueName 'Script' -Type String -Value 'powershell.exe' | Out-Null; Set-GPPrefRegistryValue -Name $gpo.DisplayName -Context Computer -Action Create -Key 'HKLM\Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Startup\0' -ValueName 'Parameters' -Type String -Value '-ExecutionPolicy Bypass -File \\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-EN.ps1' | Out-Null"

REM Configure PowerShell execution policy
powershell.exe -Command "$gpo = Get-GPO -Name 'BitLocker Disable Script'; Set-GPRegistryValue -Name $gpo.DisplayName -Key 'HKLM\Software\Policies\Microsoft\Windows\PowerShell' -ValueName 'ExecutionPolicy' -Type String -Value 'Bypass' | Out-Null"

echo GPO setup completed successfully.
echo Please ensure that:
echo 1. The network share \\SP63210003\Dist\Bitlocker is accessible to all target computers
echo 2. The BitLocker PowerShell module is installed on target computers
echo 3. The GPO is linked to the appropriate OU in Active Directory
echo 4. Network share permissions are properly configured

pause 