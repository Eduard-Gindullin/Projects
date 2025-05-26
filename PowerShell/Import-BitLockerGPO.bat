@echo off
setlocal enabledelayedexpansion

:: Check for language parameter
set "LANG=%1"
if "%LANG%"=="" (
    for /f "tokens=1 delims=." %%a in ('wmic os get locale ^| findstr "^[0-9]"') do set "LOCALE=%%a"
    if "!LOCALE!"=="1049" (
        set "LANG=ru-RU"
    ) else if "!LOCALE!"=="1036" (
        set "LANG=fr-FR"
    ) else (
        set "LANG=en-US"
    )
)

:: Messages dictionary
if "%LANG%"=="ru-RU" (
    set "MSG_ADMIN_CHECK=Проверка прав администратора..."
    set "MSG_ADMIN_REQUIRED=Требуются права администратора. Пожалуйста, запустите от имени администратора."
    set "MSG_RSAT_CHECK=Проверка установки RSAT..."
    set "MSG_RSAT_REQUIRED=RSAT не установлен. Установите Remote Server Administration Tools."
    set "MSG_CREATING_GPO=Создание групповой политики BitLocker..."
    set "MSG_SETTING_POLICY=Настройка параметров политики..."
    set "MSG_SUCCESS=Групповая политика успешно создана и настроена."
    set "MSG_ERROR=Произошла ошибка: "
    set "LOG_PREFIX=ИМПОРТ_ПОЛИТИКИ"
) else if "%LANG%"=="fr-FR" (
    set "MSG_ADMIN_CHECK=Vérification des droits d'administrateur..."
    set "MSG_ADMIN_REQUIRED=Droits d'administrateur requis. Veuillez exécuter en tant qu'administrateur."
    set "MSG_RSAT_CHECK=Vérification de l'installation RSAT..."
    set "MSG_RSAT_REQUIRED=RSAT n'est pas installé. Installez Remote Server Administration Tools."
    set "MSG_CREATING_GPO=Création de la stratégie de groupe BitLocker..."
    set "MSG_SETTING_POLICY=Configuration des paramètres de la stratégie..."
    set "MSG_SUCCESS=Stratégie de groupe créée et configurée avec succès."
    set "MSG_ERROR=Une erreur s'est produite: "
    set "LOG_PREFIX=IMPORT_STRATEGIE"
) else (
    set "MSG_ADMIN_CHECK=Checking administrator rights..."
    set "MSG_ADMIN_REQUIRED=Administrator rights required. Please run as administrator."
    set "MSG_RSAT_CHECK=Checking RSAT installation..."
    set "MSG_RSAT_REQUIRED=RSAT is not installed. Please install Remote Server Administration Tools."
    set "MSG_CREATING_GPO=Creating BitLocker Group Policy..."
    set "MSG_SETTING_POLICY=Configuring policy settings..."
    set "MSG_SUCCESS=Group Policy successfully created and configured."
    set "MSG_ERROR=An error occurred: "
    set "LOG_PREFIX=POLICY_IMPORT"
)

:: Log file setup
set "LOGFILE=%~dp0GPO_Import.log"
set "TIMESTAMP=%date:~-4%-%date:~3,2%-%date:~0,2% %time:~0,2%:%time:~3,2%:%time:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"

:: Logging function
:log
echo %TIMESTAMP% [%LOG_PREFIX%] %~1 >> "%LOGFILE%"
echo %~1
exit /b

:: Check for admin rights
echo %MSG_ADMIN_CHECK%
net session >nul 2>&1
if %errorlevel% neq 0 (
    call :log "%MSG_ADMIN_REQUIRED%"
    exit /b 1
)

:: Check for RSAT
echo %MSG_RSAT_CHECK%
powershell -Command "Get-Module -ListAvailable -Name GroupPolicy" >nul 2>&1
if %errorlevel% neq 0 (
    call :log "%MSG_RSAT_REQUIRED%"
    exit /b 1
)

:: Create and configure GPO
echo %MSG_CREATING_GPO%
powershell -Command "New-GPO -Name 'BitLocker Disable' -Comment 'Disable BitLocker encryption' | %null%" 2>nul
if %errorlevel% neq 0 (
    call :log "%MSG_ERROR%Failed to create GPO"
    exit /b 1
)

echo %MSG_SETTING_POLICY%
powershell -Command "Set-GPRegistryValue -Name 'BitLocker Disable' -Key 'HKLM\Software\Policies\Microsoft\FVE' -ValueName 'DisableDeviceEncryption' -Type DWord -Value 1" 2>nul
if %errorlevel% neq 0 (
    call :log "%MSG_ERROR%Failed to set registry value"
    exit /b 1
)

call :log "%MSG_SUCCESS%"
exit /b 0 