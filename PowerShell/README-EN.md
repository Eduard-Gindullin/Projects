# BitLocker Disable Script

## Description
This script is designed to automatically disable BitLocker encryption on all encrypted drives of a computer.
Developed for mass deployment through Group Policy (GPO).

## Requirements
- Windows PowerShell 5.1 or higher
- BitLocker PowerShell module installed
- Access to network share for logging
- Administrator rights on target computers

## File Structure
- `Disable-BitLocker-EN.ps1` - main BitLocker disable script (English version)
- `Import-BitLockerGPO-EN.bat` - GPO setup script (English version)

## File Locations
- Script: `\\SP63210003\Dist\Bitlocker\Script\Disable-BitLocker-EN.ps1`
- Logs: `\\SP63210003\Dist\Bitlocker\BitlockerLog\BitLocker_Disable.log`

## Log File Format
```
DateTime,ComputerName,DriveLetter,Status
```

### Possible Statuses:
- `SUCCESS` - BitLocker successfully disabled
- `ALREADY_DISABLED` - BitLocker was already disabled
- `FAILED` - Error while disabling BitLocker
- `CRITICAL_ERROR` - Critical script execution error
- `MODULE_NOT_FOUND` - BitLocker PowerShell module not found

## GPO Setup
1. Copy `Disable-BitLocker-EN.ps1` to `\\SP63210003\Dist\Bitlocker\Script`
2. Run `Import-BitLockerGPO-EN.bat` as domain administrator
3. Link the created "BitLocker Disable Script" GPO to the appropriate Organizational Unit (OU)

## Pre-deployment Checklist
1. Ensure that:
   - Network share `\\SP63210003\Dist\Bitlocker` is accessible to all target computers
   - BitLocker PowerShell module is installed on target computers
   - GPO is linked to the appropriate OU
   - Network share permissions are properly configured

## Troubleshooting
1. If log status is `MODULE_NOT_FOUND`:
   - Install BitLocker PowerShell module on target computer
   - Check PowerShell version
2. If log status is `FAILED`:
   - Check administrator rights
   - Check drive status
3. If no log entries are present:
   - Check network share accessibility
   - Check log folder permissions

## Security
- Script requires administrator privileges
- Ensure network share with logs is only accessible to administrators
- Regular log file archiving is recommended

## Support
When encountering issues, check:
1. BitLocker module availability
2. Access permissions
3. Network share accessibility
4. Windows Event Log 