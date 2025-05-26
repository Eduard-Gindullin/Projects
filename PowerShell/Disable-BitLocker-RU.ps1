# Скрипт для отключения шифрования BitLocker на всех дисках
# Настройка логирования
$LogPath = "\\SP63210003\Dist\Bitlocker\BitlockerLog"
$LogFile = Join-Path -Path $LogPath -ChildPath "BitLocker_Disable.log"

# Функция для записи в лог
function Write-Log {
    param($ComputerName, $DriveLetter, $Status)
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$ComputerName,$DriveLetter,$Status"
    Add-Content -Path $LogFile -Value $LogMessage
}

try {
    # Создание папки для логов, если она не существует
    if (-not (Test-Path -Path $LogPath)) {
        New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
    }

    # Проверка наличия модуля BitLocker
    $BitLockerModule = Get-Module -ListAvailable -Name BitLocker
    if (-not $BitLockerModule) {
        Write-Log -ComputerName $env:COMPUTERNAME -DriveLetter "N/A" -Status "МОДУЛЬ_НЕ_НАЙДЕН"
        exit 1
    }

    # Импорт модуля BitLocker с подавлением предупреждений
    $WarningPreference = 'SilentlyContinue'
    Import-Module BitLocker -ErrorAction Stop
    $WarningPreference = 'Continue'

    # Получение всех томов BitLocker
    $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $ComputerName = $env:COMPUTERNAME

    foreach ($Volume in $BitLockerVolumes) {
        try {
            $DriveLetter = $Volume.MountPoint

            if ($Volume.ProtectionStatus -eq "On") {
                # Отключение BitLocker
                Disable-BitLocker -MountPoint $DriveLetter -ErrorAction Stop
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "УСПЕШНО"
            }
            else {
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "УЖЕ_ОТКЛЮЧЕН"
            }
        }
        catch {
            Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "ОШИБКА"
        }
    }
}
catch {
    Write-Log -ComputerName $env:COMPUTERNAME -DriveLetter "N/A" -Status "КРИТИЧЕСКАЯ_ОШИБКА"
    exit 1
} 