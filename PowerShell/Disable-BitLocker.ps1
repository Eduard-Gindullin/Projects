[CmdletBinding()]
param (
    [Parameter()]
    [ValidateSet("ru-RU", "en-US", "fr-FR")]
    [string]$Culture = (Get-Culture).Name
)

# Словарь локализации / Localization dictionary / Dictionnaire de localisation
$Messages = @{
    'ru-RU' = @{
        'DECRYPTING' = 'РАСШИФРОВКА'
        'ENCRYPTED' = 'ЗАШИФРОВАНО'
        'DECRYPTED' = 'РАСШИФРОВАНО'
        'ERROR' = 'ОШИБКА'
        'STARTING_DISABLE' = 'НАЧАЛО_ОТКЛЮЧЕНИЯ'
        'ALREADY_DISABLED' = 'УЖЕ_ОТКЛЮЧЕН'
        'DECRYPTION_STARTED' = 'РАСШИФРОВКА_ЗАПУЩЕНА_ПРОДОЛЖЕНИЕ_В_ФОНЕ'
        'MONITORING_TASK_CREATED' = 'СОЗДАНА_ЗАДАЧА_МОНИТОРИНГА'
        'MONITORING_COMPLETED' = 'МОНИТОРИНГ_ЗАВЕРШЕН_ЗАДАЧА_УДАЛЕНА'
        'STATUS_CHECK_ERROR' = 'ОШИБКА_ПРОВЕРКИ_СТАТУСА'
        'TASK_REMOVAL_ERROR' = 'ОШИБКА_УДАЛЕНИЯ_ЗАДАЧИ'
        'CRITICAL_ERROR' = 'КРИТИЧЕСКАЯ_ОШИБКА'
    }
    'en-US' = @{
        'DECRYPTING' = 'DECRYPTING'
        'ENCRYPTED' = 'ENCRYPTED'
        'DECRYPTED' = 'DECRYPTED'
        'ERROR' = 'ERROR'
        'STARTING_DISABLE' = 'STARTING_DISABLE'
        'ALREADY_DISABLED' = 'ALREADY_DISABLED'
        'DECRYPTION_STARTED' = 'DECRYPTION_STARTED_CONTINUING_IN_BACKGROUND'
        'MONITORING_TASK_CREATED' = 'MONITORING_TASK_CREATED'
        'MONITORING_COMPLETED' = 'MONITORING_COMPLETED_TASK_REMOVED'
        'STATUS_CHECK_ERROR' = 'STATUS_CHECK_ERROR'
        'TASK_REMOVAL_ERROR' = 'TASK_REMOVAL_ERROR'
        'CRITICAL_ERROR' = 'CRITICAL_ERROR'
    }
    'fr-FR' = @{
        'DECRYPTING' = 'DECHIFFREMENT'
        'ENCRYPTED' = 'CHIFFRE'
        'DECRYPTED' = 'DECHIFFRE'
        'ERROR' = 'ERREUR'
        'STARTING_DISABLE' = 'DEBUT_DESACTIVATION'
        'ALREADY_DISABLED' = 'DEJA_DESACTIVE'
        'DECRYPTION_STARTED' = 'DECHIFFREMENT_DEMARRE_CONTINUE_EN_ARRIERE_PLAN'
        'MONITORING_TASK_CREATED' = 'TACHE_DE_SURVEILLANCE_CREEE'
        'MONITORING_COMPLETED' = 'SURVEILLANCE_TERMINEE_TACHE_SUPPRIMEE'
        'STATUS_CHECK_ERROR' = 'ERREUR_VERIFICATION_STATUT'
        'TASK_REMOVAL_ERROR' = 'ERREUR_SUPPRESSION_TACHE'
        'CRITICAL_ERROR' = 'ERREUR_CRITIQUE'
    }
}

# Функция для получения локализованного сообщения / Function to get localized message
function Get-LocalizedMessage {
    param (
        [string]$Key
    )
    return $Messages[$Culture][$Key]
}

# Функция для проверки необходимости мониторинга / Function to check if monitoring is still required
function Test-MonitoringRequired {
    param (
        [string]$ComputerName
    )
    
    try {
        $content = Get-Content -Path $StatusFile | ConvertFrom-Csv
        $computerEntries = $content | Where-Object { $_.ComputerName -eq $ComputerName }
        
        if (-not $computerEntries) {
            return $false
        }
        
        foreach ($entry in $computerEntries) {
            if ($entry.Status -eq (Get-LocalizedMessage 'DECRYPTING') -or 
                $entry.Status -eq (Get-LocalizedMessage 'ENCRYPTED')) {
                return $true
            }
        }
        
        return $false
    }
    catch {
        $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'STATUS_CHECK_ERROR')
        Write-Log -ComputerName $ComputerName -DriveLetter "N/A" -Status $errorMessage
        return $true
    }
}

# Функция для очистки задачи мониторинга / Function to clean up monitoring task
function Remove-MonitoringTask {
    param (
        [string]$ComputerName
    )
    
    try {
        $taskName = "BitLocker Monitoring"
        $task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
        
        if ($task) {
            Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            Write-Log -ComputerName $ComputerName -DriveLetter "N/A" -Status (Get-LocalizedMessage 'MONITORING_COMPLETED')
        }
    }
    catch {
        $errorMessage = "{0}: $($_.Exception.Message)" -f (Get-LocalizedMessage 'TASK_REMOVAL_ERROR')
        Write-Log -ComputerName $ComputerName -DriveLetter "N/A" -Status $errorMessage
    }
}

try {
    $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $ComputerName = $env:COMPUTERNAME
    $monitoringRequired = $false

    foreach ($Volume in $BitLockerVolumes) {
        try {
            $DriveLetter = $Volume.MountPoint

            if ($Volume.ProtectionStatus -eq "On") {
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'STARTING_DISABLE')
                Update-DecryptionStatus -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'STARTING_DISABLE') -Progress "0"
                
                Disable-BitLocker -MountPoint $DriveLetter -ErrorAction Stop

                $maxAttempts = 3
                $sleepSeconds = 10
                $attempt = 0

                do {
                    Start-Sleep -Seconds $sleepSeconds
                    $decryptionComplete = Update-VolumeStatus -DriveLetter $DriveLetter -ComputerName $ComputerName
                    $attempt++
                } while (-not $decryptionComplete -and $attempt -lt $maxAttempts)

                if (-not $decryptionComplete) {
                    Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'DECRYPTION_STARTED')
                    $monitoringRequired = $true
                }
            }
            else {
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ALREADY_DISABLED')
                Update-DecryptionStatus -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'DECRYPTED') -Progress "100"
            }
        }
        catch {
            $errorMessage = "{0}_$($_.Exception.Message)" -f (Get-LocalizedMessage 'ERROR')
            Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status $errorMessage
            Update-DecryptionStatus -ComputerName $ComputerName -DriveLetter $DriveLetter -Status (Get-LocalizedMessage 'ERROR') -Progress "0"
            $monitoringRequired = $true
        }
    }

    $taskName = "BitLocker Monitoring"
    $taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

    if ($monitoringRequired) {
        if (-not $taskExists) {
            $action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
                -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"& {
                    Import-Module BitLocker
                    `$volumes = Get-BitLockerVolume
                    foreach (`$vol in `$volumes) {
                        . '$PSCommandPath' -Culture '$Culture'
                        Update-VolumeStatus -DriveLetter `$vol.MountPoint -ComputerName '$ComputerName'
                    }
                    if (-not (Test-MonitoringRequired -ComputerName '$ComputerName')) {
                        Remove-MonitoringTask -ComputerName '$ComputerName'
                    }
                }`""
            
            $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 10)
            $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
            
            Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal
            Write-Log -ComputerName $ComputerName -DriveLetter "N/A" -Status (Get-LocalizedMessage 'MONITORING_TASK_CREATED')
        }
    }
    else {
        if ($taskExists) {
            Remove-MonitoringTask -ComputerName $ComputerName
        }
    }
}
catch {
    $errorMessage = "{0}_$($_.Exception.Message)" -f (Get-LocalizedMessage 'CRITICAL_ERROR')
    Write-Log -ComputerName $env:COMPUTERNAME -DriveLetter "N/A" -Status $errorMessage
    exit 1
} 