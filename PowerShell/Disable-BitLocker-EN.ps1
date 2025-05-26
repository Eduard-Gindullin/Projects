# Script to disable BitLocker encryption on all drives
# Logging configuration
$LogPath = "\\SP63210003\Dist\Bitlocker\BitlockerLog"
$LogFile = Join-Path -Path $LogPath -ChildPath "BitLocker_Disable.log"

# Function to write log
function Write-Log {
    param($ComputerName, $DriveLetter, $Status)
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$ComputerName,$DriveLetter,$Status"
    Add-Content -Path $LogFile -Value $LogMessage
}

try {
    # Create log directory if it doesn't exist
    if (-not (Test-Path -Path $LogPath)) {
        New-Item -ItemType Directory -Path $LogPath -Force | Out-Null
    }

    # Check if BitLocker module is available
    $BitLockerModule = Get-Module -ListAvailable -Name BitLocker
    if (-not $BitLockerModule) {
        Write-Log -ComputerName $env:COMPUTERNAME -DriveLetter "N/A" -Status "MODULE_NOT_FOUND"
        exit 1
    }

    # Import BitLocker module and suppress verb warnings
    $WarningPreference = 'SilentlyContinue'
    Import-Module BitLocker -ErrorAction Stop
    $WarningPreference = 'Continue'

    # Get all BitLocker volumes
    $BitLockerVolumes = Get-BitLockerVolume -ErrorAction Stop
    $ComputerName = $env:COMPUTERNAME

    foreach ($Volume in $BitLockerVolumes) {
        try {
            $DriveLetter = $Volume.MountPoint

            if ($Volume.ProtectionStatus -eq "On") {
                # Disable BitLocker
                Disable-BitLocker -MountPoint $DriveLetter -ErrorAction Stop
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "SUCCESS"
            }
            else {
                Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "ALREADY_DISABLED"
            }
        }
        catch {
            Write-Log -ComputerName $ComputerName -DriveLetter $DriveLetter -Status "FAILED"
        }
    }
}
catch {
    Write-Log -ComputerName $env:COMPUTERNAME -DriveLetter "N/A" -Status "CRITICAL_ERROR"
    exit 1
} 