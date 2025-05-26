@echo off
REM Скрипт для импорта настроек групповой политики для отключения BitLocker

echo Создание групповой политики для скрипта отключения BitLocker...

REM Создание новой групповой политики
powershell.exe -Command "New-GPO -Name 'Отключение BitLocker' -Comment 'Автоматическое отключение BitLocker при запуске'"

REM Проверка наличия скрипта
if not exist "\\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-RU.ps1" (
    echo Ошибка: Скрипт не найден: \\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-RU.ps1
    echo Убедитесь, что скрипт находится в указанной папке перед настройкой GPO
    pause
    exit /b 1
)

REM Проверка и создание папки для логов, если она не существует
if not exist "\\SP63210003\Dist\Bitlocker\BitlockerLog" mkdir "\\SP63210003\Dist\Bitlocker\BitlockerLog"

REM Настройка запуска PowerShell скрипта через групповую политику
powershell.exe -Command "$gpo = Get-GPO -Name 'Отключение BitLocker'; Set-GPPrefRegistryValue -Name $gpo.DisplayName -Context Computer -Action Create -Key 'HKLM\Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Startup\0' -ValueName 'Script' -Type String -Value 'powershell.exe' | Out-Null; Set-GPPrefRegistryValue -Name $gpo.DisplayName -Context Computer -Action Create -Key 'HKLM\Software\Microsoft\Windows\CurrentVersion\Group Policy\Scripts\Startup\0' -ValueName 'Parameters' -Type String -Value '-ExecutionPolicy Bypass -File \\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-RU.ps1' | Out-Null"

REM Настройка разрешений для выполнения скриптов PowerShell
powershell.exe -Command "$gpo = Get-GPO -Name 'Отключение BitLocker'; Set-GPRegistryValue -Name $gpo.DisplayName -Key 'HKLM\Software\Policies\Microsoft\Windows\PowerShell' -ValueName 'ExecutionPolicy' -Type String -Value 'Bypass' | Out-Null"

echo Настройка групповой политики успешно завершена.
echo Пожалуйста, проверьте:
echo 1. Сетевая папка \\SP63210003\Dist\Bitlocker доступна всем целевым компьютерам
echo 2. Модуль BitLocker PowerShell установлен на целевых компьютерах
echo 3. Групповая политика привязана к соответствующему подразделению в Active Directory
echo 4. Правильно настроены разрешения для сетевой папки

pause 