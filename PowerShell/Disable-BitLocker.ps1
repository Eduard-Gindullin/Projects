# Script for BitLocker encryption management
# Скрипт для управления шифрованием BitLocker

# Force UTF-8 encoding for all output
# Установка кодировки UTF-8 для всего вывода
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Set default encoding for Export-Csv
# Установка кодировки по умолчанию для Export-Csv
$PSDefaultParameterValues['Export-Csv:Encoding'] = 'UTF8'

# Check if running with administrative privileges
# Проверка на наличие административных прав
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "This script requires administrative privileges. Please run as Administrator." -ForegroundColor Red
    exit 1
}

# Define log file paths
# Определение путей к файлам журнала
$NetworkLogPath = "\\SP63210003\Dist\Bitlocker\BitlockerLog"
$NetworkLogFile = Join-Path $NetworkLogPath "BitLocker_Status.csv"

# Status messages
# Статусные сообщения
$Messages = @{
    'DECRYPTING' = 'DECRYPTING'
    'ENCRYPTED' = 'ENCRYPTED'
    'DECRYPTED' = 'DECRYPTED'
    'ERROR' = 'ERROR'
    'STARTING_DISABLE' = 'STARTING_DISABLE'
    'ALREADY_DISABLED' = 'ALREADY_DISABLED'
    'COMPLETED' = 'COMPLETED'
}

# Function to check TPM status
# Функция проверки статуса TPM
function Get-TPMStatus {
    try {
        $tpm = Get-WmiObject -Class Win32_Tpm -Namespace root\CIMV2\Security\MicrosoftTpm
        if ($null -eq $tpm) {
            return "TPM_MISSING"
        }
        return "TPM_PRESENT"
    }
    catch {
        return "TPM_MISSING"
    }
}

# Function to check last log entry status
# Функция для проверки статуса последней записи в логе
function Get-LastLogStatus {
    param (
        [string]$ComputerName
    )
    
    try {
        if (Test-Path $NetworkLogFile) {
            $lastEntry = Import-Csv -Path $NetworkLogFile -Encoding UTF8 | 
                        Where-Object { $_.ComputerName -eq $ComputerName } |
                        Sort-Object { [DateTime]::ParseExact($_.Timestamp, "yyyy-MM-dd HH:mm:ss", $null) } -Descending |
                        Select-Object -First 1
            
            if ($lastEntry) {
                return $lastEntry.Status
            }
        }
    }
    catch {
        Write-Host "Error reading last log status: $($_.Exception.Message)" -ForegroundColor Yellow
    }
    return $null
}

# Function to write log
# Функция для записи в журнал
function Write-Log {
    param (
        [string]$DriveLetter,
        [string]$Status,
        [string]$EncryptionPercentage = "N/A",
        [string]$TPMStatus = "N/A"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $computerName = $env:COMPUTERNAME
    
    # Check if we already have a COMPLETED status for this computer
    $lastStatus = Get-LastLogStatus -ComputerName $computerName
    if ($lastStatus -eq $Messages['COMPLETED'] -and $Status -eq $Messages['COMPLETED']) {
        Write-Host "Skipping duplicate COMPLETED status for $computerName" -ForegroundColor Yellow
        return
    }
    
    # Write to console
    # Вывод в консоль
    Write-Host "[$timestamp] $computerName - Drive $DriveLetter : $Status ($EncryptionPercentage%) [TPM: $TPMStatus]"
    
    # Create new entry
    # Создание новой записи
    $newEntry = [PSCustomObject]@{
        Timestamp = $timestamp
        ComputerName = $computerName
        DriveLetter = $DriveLetter
        TPMStatus = $TPMStatus
        EncryptionPercentage = $EncryptionPercentage
        Status = $Status
    }
    
    # Update CSV file with file lock handling
    # Обновление CSV файла с обработкой блокировки
    $mutex = New-Object System.Threading.Mutex($false, "Global\BitLockerLogMutex")
    try {
        $mutex.WaitOne(10000) | Out-Null # Wait up to 10 seconds for lock
        
        if (Test-Path $NetworkLogFile) {
            try {
                # Read all entries except current computer's entry
                $logContent = @(Import-Csv -Path $NetworkLogFile -Encoding UTF8 | 
                              Where-Object { $_.ComputerName -ne $computerName })
                $logContent += $newEntry
                
                # Sort entries by timestamp (newest first) and save
                $logContent | Sort-Object { [DateTime]::ParseExact($_.Timestamp, "yyyy-MM-dd HH:mm:ss", $null) } -Descending |
                    Export-Csv -Path $NetworkLogFile -NoTypeInformation -Encoding UTF8 -Force
            }
            catch {
                Write-Host "Error updating log file: $($_.Exception.Message)" -ForegroundColor Red
                throw
            }
        } else {
            # Create new log file with header and first entry
            $newEntry | Export-Csv -Path $NetworkLogFile -NoTypeInformation -Encoding UTF8 -Force
        }
    }
    finally {
        if ($mutex) {
            $mutex.ReleaseMutex()
        }
    }
}

# Function to check if all volumes are decrypted
# Функция для проверки, все ли тома расшифрованы
function Test-AllVolumesDecrypted {
    try {
        $volumes = Get-BitLockerVolume
        foreach ($volume in $volumes) {
            Write-Host "Checking volume $($volume.MountPoint):" -ForegroundColor Cyan
            Write-Host "  Protection Status: $($volume.ProtectionStatus)" -ForegroundColor Cyan
            Write-Host "  Volume Status: $($volume.VolumeStatus)" -ForegroundColor Cyan
            Write-Host "  Encryption Percentage: $($volume.EncryptionPercentage)%" -ForegroundColor Cyan
            
            if ($volume.ProtectionStatus -eq "On" -or 
                $volume.VolumeStatus -eq "EncryptionInProgress" -or 
                $volume.VolumeStatus -eq "DecryptionInProgress" -or
                ($volume.ProtectionStatus -eq "Off" -and $volume.EncryptionPercentage -gt 0)) {
                return $false
            }
        }
        return $true
    }
    catch {
        Write-Host "Error in Test-AllVolumesDecrypted: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main script execution
# Основное выполнение скрипта
try {
    # Check BitLocker module availability
    # Проверка доступности модуля BitLocker
    if (-not (Get-Command -Name 'Get-BitLockerVolume' -ErrorAction SilentlyContinue)) {
        Write-Host "BitLocker PowerShell module not available. Please check if BitLocker is installed." -ForegroundColor Red
        exit 1
    }
    
    # Check if we already have a COMPLETED status
    $lastStatus = Get-LastLogStatus -ComputerName $env:COMPUTERNAME
    if ($lastStatus -eq $Messages['COMPLETED']) {
        Write-Host "BitLocker decryption already completed for this computer. Exiting." -ForegroundColor Green
        exit 0
    }
    
    $ComputerName = $env:COMPUTERNAME
    $tpmStatus = Get-TPMStatus
    $logUpdateInterval = New-TimeSpan -Minutes 5
    $lastLogUpdate = [DateTime]::MinValue
    
    # If BitLocker is not enabled and TPM is missing, log it and exit
    $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $hasEncryptedVolumes = $false
    foreach ($Volume in $BitLockerVolumes) {
        if ($Volume.ProtectionStatus -eq "On" -or 
            $Volume.VolumeStatus -eq "DecryptionInProgress" -or
            ($Volume.ProtectionStatus -eq "Off" -and $Volume.EncryptionPercentage -gt 0)) {
            $hasEncryptedVolumes = $true
            break
        }
    }
    
    if (-not $hasEncryptedVolumes) {
        Write-Host "No encrypted volumes found. Logging status and exiting." -ForegroundColor Green
        Write-Log -DriveLetter "C:" -Status $Messages['ALREADY_DISABLED'] -EncryptionPercentage "0" -TPMStatus $tpmStatus
        Write-Log -DriveLetter "C:" -Status $Messages['COMPLETED'] -EncryptionPercentage "0" -TPMStatus $tpmStatus
        exit 0
    }
    
    # Start decryption for all encrypted volumes
    foreach ($Volume in $BitLockerVolumes) {
        if ($Volume.ProtectionStatus -eq "On") {
            Write-Host "Starting decryption for volume $($Volume.MountPoint)..." -ForegroundColor Yellow
            Write-Log -DriveLetter $Volume.MountPoint -Status $Messages['STARTING_DISABLE'] -TPMStatus $tpmStatus
            Disable-BitLocker -MountPoint $Volume.MountPoint -ErrorAction Stop
        }
    }
    
    # Monitor decryption progress
    Write-Host "Starting decryption monitoring..." -ForegroundColor Cyan
    while ($true) {
        $currentTime = Get-Date
        $shouldUpdateLog = ($currentTime - $lastLogUpdate) -ge $logUpdateInterval
        $allDecrypted = $true
        
        $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
        foreach ($Volume in $BitLockerVolumes) {
            $status = ""
            $encryptionPercentage = $Volume.EncryptionPercentage
            
            if ($Volume.ProtectionStatus -eq "On") {
                $status = $Messages['ENCRYPTED']
                $allDecrypted = $false
            }
            elseif ($Volume.VolumeStatus -eq "DecryptionInProgress" -or 
                   ($Volume.ProtectionStatus -eq "Off" -and $encryptionPercentage -gt 0)) {
                $status = $Messages['DECRYPTING']
                $allDecrypted = $false
            }
            elseif ($Volume.VolumeStatus -eq "FullyDecrypted" -or 
                   ($Volume.ProtectionStatus -eq "Off" -and $encryptionPercentage -eq 0)) {
                $status = $Messages['DECRYPTED']
            }
            
            # Update console always
            Write-Host "[$($currentTime.ToString('yyyy-MM-dd HH:mm:ss'))] Volume $($Volume.MountPoint): $status ($encryptionPercentage%) [TPM: $tpmStatus]" -ForegroundColor Cyan
            
            # Update log only at intervals
            if ($shouldUpdateLog) {
                Write-Log -DriveLetter $Volume.MountPoint -Status $status -EncryptionPercentage $encryptionPercentage -TPMStatus $tpmStatus
            }
        }
        
        if ($shouldUpdateLog) {
            $lastLogUpdate = $currentTime
        }
        
        # If all volumes are decrypted, write final status and exit
        if ($allDecrypted) {
            Write-Host "All volumes have been decrypted!" -ForegroundColor Green
            Write-Log -DriveLetter "C:" -Status $Messages['COMPLETED'] -EncryptionPercentage "0" -TPMStatus $tpmStatus
            exit 0
        }
        
        # Wait for 30 seconds before next check
        Start-Sleep -Seconds 30
    }
}
catch {
    Write-Log -DriveLetter "N/A" -Status $Messages['ERROR'] -TPMStatus (Get-TPMStatus)
    Write-Host "Critical error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} 