# Get culture parameter and arguments
param(
    [string]$Culture = (Get-Culture).Name
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

if ($Culture -notin @("ru-RU", "en-US", "fr-FR")) { 
    $Culture = "en-US" 
}

# Define log file path
$LogPath = "\\SP63210003\Dist\Bitlocker\BitlockerLog"
$LogFile = Join-Path $LogPath "BitLocker_Status.csv"

# Create log directory if it doesn't exist
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
}

# Create log file if it doesn't exist
if (-not (Test-Path $LogFile)) {
    "Timestamp,ComputerName,DriveLetter,Status,EncryptionPercentage" | Out-File -FilePath $LogFile -Encoding UTF8
}

# Messages dictionary
$RuMessages = @"
{
    'ENCRYPTING': 'ШИФРОВАНИЕ',
    'ENCRYPTED': 'ЗАШИФРОВАН',
    'DECRYPTED': 'РАСШИФРОВАН',
    'ERROR': 'ОШИБКА',
    'STARTING_ENABLE': 'НАЧАЛО_ВКЛЮЧЕНИЯ',
    'ALREADY_ENABLED': 'УЖЕ_ВКЛЮЧЕН',
    'ENCRYPTION_STARTED': 'ШИФРОВАНИЕ_ЗАПУЩЕНО_ПРОДОЛЖЕНИЕ_В_ФОНЕ',
    'MONITORING_TASK_CREATED': 'СОЗДАНА_ЗАДАЧА_МОНИТОРИНГА',
    'MONITORING_COMPLETED': 'МОНИТОРИНГ_ЗАВЕРШЕН_ЗАДАЧА_УДАЛЕНА',
    'STATUS_CHECK_ERROR': 'ОШИБКА_ПРОВЕРКИ_СТАТУСА',
    'TASK_REMOVAL_ERROR': 'ОШИБКА_УДАЛЕНИЯ_ЗАДАЧИ',
    'CRITICAL_ERROR': 'КРИТИЧЕСКАЯ_ОШИБКА',
    'MONITORING': 'МОНИТОРИНГ',
    'KEY_BACKUP': 'СОХРАНЕНИЕ_КЛЮЧА_ВОССТАНОВЛЕНИЯ',
    'KEY_BACKUP_ERROR': 'ОШИБКА_СОХРАНЕНИЯ_КЛЮЧА'
}
"@ | ConvertFrom-Json

$EnMessages = @"
{
    'ENCRYPTING': 'ENCRYPTING',
    'ENCRYPTED': 'ENCRYPTED',
    'DECRYPTED': 'DECRYPTED',
    'ERROR': 'ERROR',
    'STARTING_ENABLE': 'STARTING_ENABLE',
    'ALREADY_ENABLED': 'ALREADY_ENABLED',
    'ENCRYPTION_STARTED': 'ENCRYPTION_STARTED_CONTINUING_IN_BACKGROUND',
    'MONITORING_TASK_CREATED': 'MONITORING_TASK_CREATED',
    'MONITORING_COMPLETED': 'MONITORING_COMPLETED_TASK_REMOVED',
    'STATUS_CHECK_ERROR': 'STATUS_CHECK_ERROR',
    'TASK_REMOVAL_ERROR': 'TASK_REMOVAL_ERROR',
    'CRITICAL_ERROR': 'CRITICAL_ERROR',
    'MONITORING': 'MONITORING',
    'KEY_BACKUP': 'SAVING_RECOVERY_KEY',
    'KEY_BACKUP_ERROR': 'KEY_BACKUP_ERROR'
}
"@ | ConvertFrom-Json

$FrMessages = @"
{
    'ENCRYPTING': 'CHIFFREMENT',
    'ENCRYPTED': 'CHIFFRE',
    'DECRYPTED': 'DECHIFFRE',
    'ERROR': 'ERREUR',
    'STARTING_ENABLE': 'DEBUT_ACTIVATION',
    'ALREADY_ENABLED': 'DEJA_ACTIVE',
    'ENCRYPTION_STARTED': 'CHIFFREMENT_DEMARRE_CONTINUE_EN_ARRIERE_PLAN',
    'MONITORING_TASK_CREATED': 'TACHE_DE_SURVEILLANCE_CREEE',
    'MONITORING_COMPLETED': 'SURVEILLANCE_TERMINEE_TACHE_SUPPRIMEE',
    'STATUS_CHECK_ERROR': 'ERREUR_VERIFICATION_STATUT',
    'TASK_REMOVAL_ERROR': 'ERREUR_SUPPRESSION_TACHE',
    'CRITICAL_ERROR': 'ERREUR_CRITIQUE',
    'MONITORING': 'SURVEILLANCE',
    'KEY_BACKUP': 'SAUVEGARDE_CLE_RECUPERATION',
    'KEY_BACKUP_ERROR': 'ERREUR_SAUVEGARDE_CLE'
}
"@ | ConvertFrom-Json

$Messages = @{
    'ru-RU' = $RuMessages
    'en-US' = $EnMessages
    'fr-FR' = $FrMessages
}

function Get-LocalizedMessage {
    param (
        [string]$Key
    )
    return $Messages[$Culture].$Key
}

function Write-Log {
    param (
        [string]$DriveLetter,
        [string]$Status,
        [string]$EncryptionPercentage = "N/A"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "$timestamp,$env:COMPUTERNAME,$DriveLetter,$Status,$EncryptionPercentage"
    
    # Write to console
    Write-Host "[$timestamp] $env:COMPUTERNAME - Drive $DriveLetter : $Status ($EncryptionPercentage%)"
    
    # Write to CSV file with file lock handling
    $mutex = New-Object System.Threading.Mutex($false, "Global\BitLockerLogMutex")
    try {
        $mutex.WaitOne() | Out-Null
        $logEntry | Out-File -FilePath $LogFile -Append -Encoding UTF8
    }
    finally {
        $mutex.ReleaseMutex()
    }
}

function Update-LogStatus {
    param (
        [string]$ComputerName,
        [string]$Status
    )
    
    $mutex = New-Object System.Threading.Mutex($false, "Global\BitLockerLogMutex")
    try {
        $mutex.WaitOne() | Out-Null
        
        # Read existing log content
        $logContent = Import-Csv -Path $LogFile
        
        # Create temporary file
        $tempFile = [System.IO.Path]::GetTempFileName()
        
        # Process each line
        $logContent | ForEach-Object {
            if ($_.ComputerName -eq $ComputerName) {
                # Update status for matching computer
                $_ | Add-Member -MemberType NoteProperty -Name "Status" -Value $Status -Force
            }
            $_ | Export-Csv -Path $tempFile -NoTypeInformation -Append
        }
        
        # Replace original file with updated content
        Move-Item -Path $tempFile -Destination $LogFile -Force
    }
    finally {
        $mutex.ReleaseMutex()
    }
}

function Test-MonitoringRequired {
    param (
        [string]$ComputerName
    )
    
    try {
        $content = Get-Content -Path $LogFile | ConvertFrom-Csv
        $computerEntries = $content | Where-Object { $_.ComputerName -eq $ComputerName }
        
        if (-not $computerEntries) {
            return $false
        }
        
        foreach ($entry in $computerEntries) {
            if ($entry.Status -eq (Get-LocalizedMessage 'ENCRYPTING') -or 
                $entry.Status -eq (Get-LocalizedMessage 'DECRYPTED')) {
                return $true
            }
        }
        
        return $false
    }
    catch {
        $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'STATUS_CHECK_ERROR')
        Write-Log -DriveLetter "N/A" -Status $errorMessage
        return $true
    }
}

function Remove-MonitoringTask {
    param (
        [string]$ComputerName
    )
    
    try {
        $taskName = "BitLocker Monitoring"
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        
        if ($task) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Log -DriveLetter "N/A" -Status (Get-LocalizedMessage 'MONITORING_COMPLETED')
        }
    }
    catch {
        $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'TASK_REMOVAL_ERROR')
        Write-Log -DriveLetter "N/A" -Status $errorMessage
    }
}

function Update-VolumeStatus {
    param (
        [string]$DriveLetter,
        [string]$ComputerName
    )
    
    try {
        $volume = Get-BitLockerVolume -MountPoint $DriveLetter -ErrorAction Stop
        $encryptionPercentage = $volume.EncryptionPercentage
        
        if ($volume.VolumeStatus -eq "FullyEncrypted") {
            Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ENCRYPTED') -EncryptionPercentage "100"
            return $true
        }
        elseif ($volume.VolumeStatus -eq "EncryptionInProgress") {
            Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ENCRYPTING') -EncryptionPercentage $encryptionPercentage
            return $false
        }
        else {
            Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'MONITORING') -EncryptionPercentage $encryptionPercentage
            return $false
        }
    }
    catch {
        Write-Log -DriveLetter $DriveLetter -Status ((Get-LocalizedMessage 'ERROR') + ": $($_.Exception.Message)") -EncryptionPercentage "N/A"
        return $false
    }
}

try {
    $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $ComputerName = $env:COMPUTERNAME
    $monitoringRequired = $false
    $allVolumesEncrypted = $true

    foreach ($Volume in $BitLockerVolumes) {
        try {
            $DriveLetter = $Volume.MountPoint

            if ($Volume.ProtectionStatus -eq "Off") {
                $allVolumesEncrypted = $false
                Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'STARTING_ENABLE')
                
                # Backup recovery key to AD
                try {
                    Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'KEY_BACKUP')
                    $BLV = Enable-BitLocker -MountPoint $DriveLetter -EncryptionMethod XtsAes256 -UsedSpaceOnly -SkipHardwareTest -RecoveryPasswordProtector
                    Backup-BitLockerKeyProtector -MountPoint $DriveLetter -KeyProtectorId $BLV.KeyProtector[0].KeyProtectorId
                }
                catch {
                    Write-Log -DriveLetter $DriveLetter -Status ((Get-LocalizedMessage 'KEY_BACKUP_ERROR') + ": $($_.Exception.Message)")
                    continue
                }

                $maxAttempts = 3
                $sleepSeconds = 10
                $attempt = 0

                do {
                    Start-Sleep -Seconds $sleepSeconds
                    $encryptionComplete = Update-VolumeStatus -DriveLetter $DriveLetter -ComputerName $ComputerName
                    $attempt++
                } while (-not $encryptionComplete -and $attempt -lt $maxAttempts)

                if (-not $encryptionComplete) {
                    Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ENCRYPTION_STARTED')
                    $monitoringRequired = $true
                    $allVolumesEncrypted = $false
                }
            }
            else {
                Write-Log -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ALREADY_ENABLED') -EncryptionPercentage "100"
            }
        }
        catch {
            $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'ERROR')
            Write-Log -DriveLetter $DriveLetter -Status $errorMessage -EncryptionPercentage "N/A"
            $monitoringRequired = $true
            $allVolumesEncrypted = $false
        }
    }

    if ($allVolumesEncrypted) {
        Update-LogStatus -ComputerName $ComputerName -Status "COMPLETED"
    }

    if ($monitoringRequired) {
        $taskName = "BitLocker Monitoring"
        $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

        if (-not $taskExists) {
            $scriptPath = $MyInvocation.MyCommand.Path
            $monitoringScript = @"
Import-Module BitLocker
`$volumes = Get-BitLockerVolume
foreach (`$vol in `$volumes) {
    & '$scriptPath' -Culture '$Culture'
    Update-VolumeStatus -DriveLetter `$vol.MountPoint -ComputerName '$ComputerName'
}
if (-not (Test-MonitoringRequired -ComputerName '$ComputerName')) {
    Remove-MonitoringTask -ComputerName '$ComputerName'
}
"@
            $bytes = [System.Text.Encoding]::Unicode.GetBytes($monitoringScript)
            $encodedCommand = [Convert]::ToBase64String($bytes)
            
            $action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -EncodedCommand $encodedCommand"
            $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10)
            $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal
            Write-Log -DriveLetter "N/A" -Status (Get-LocalizedMessage 'MONITORING_TASK_CREATED')
        }
    }
    else {
        $taskExists = Get-ScheduledTask -TaskName "BitLocker Monitoring" -ErrorAction SilentlyContinue
        if ($taskExists) {
            Remove-MonitoringTask -ComputerName $ComputerName
        }
    }
}
catch {
    $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'CRITICAL_ERROR')
    Write-Log -DriveLetter "N/A" -Status $errorMessage -EncryptionPercentage "N/A"
    exit 1
} 