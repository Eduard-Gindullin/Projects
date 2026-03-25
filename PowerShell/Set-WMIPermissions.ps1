# Final-WMIPermissions-Working.ps1
# Исправленная версия с правильной конвертацией SID

$namespace = "ROOT\CIMV2"
$groups = @(
    "GDLRU-BELEBEY-BMK-Administrators-Level2",
    "GDLRU-MOSCOW-BEV-Administrators-Level2",
    "GDLRU-DC1-SFD_RUSSIA-Administrators-Level2",
    "GDLRU-UFA-AGRO2000-Administrators-Level2"
)
$fullAccessMask = 393279  # Полные права WMI (CCSWWP)

# Функция конвертации строкового SID в массив байтов
function Convert-SIDStringToBytes {
    param([string]$SIDString)
    
    try {
        $sid = New-Object System.Security.Principal.SecurityIdentifier($SIDString)
        $binarySID = New-Object byte[] $sid.BinaryLength
        $sid.GetBinaryForm($binarySID, 0)
        return $binarySID
    } catch {
        Write-Error "Ошибка конвертации SID: $($_.Exception.Message)"
        return $null
    }
}

function Get-GroupSID {
    param([string]$GroupName)
    
    try {
        $ntAccount = New-Object System.Security.Principal.NTAccount($GroupName)
        $sid = $ntAccount.Translate([System.Security.Principal.SecurityIdentifier])
        return @{
            String = $sid.Value
            Binary = Convert-SIDStringToBytes -SIDString $sid.Value
        }
    } catch {
        Write-Error "Не удалось получить SID для группы $GroupName : $($_.Exception.Message)"
        return $null
    }
}

function Get-WMISecurityDescriptor {
    param([string]$Namespace)
    
    $sd = Get-WmiObject -Namespace $Namespace -Class __SystemSecurity -ErrorAction Stop
    $method = $sd.PSBase.GetMethodParameters("GetSecurityDescriptor")
    $result = $sd.PSBase.InvokeMethod("GetSecurityDescriptor", $method, $null)
    
    if ($result.ReturnValue -ne 0) {
        throw "Ошибка получения дескриптора: $($result.ReturnValue)"
    }
    
    return @{
        SecurityObject = $sd
        Descriptor = $result.Descriptor
    }
}

function Set-WMISecurityDescriptor {
    param(
        [System.Management.ManagementObject]$SecurityObject,
        [System.Management.ManagementBaseObject]$Descriptor
    )
    
    $method = $SecurityObject.PSBase.GetMethodParameters("SetSecurityDescriptor")
    $method.Descriptor = $Descriptor
    $result = $SecurityObject.PSBase.InvokeMethod("SetSecurityDescriptor", $method, $null)
    
    return $result.ReturnValue
}

function Add-WMIPermission {
    param(
        [string]$GroupName,
        [hashtable]$SIDInfo,
        [int]$AccessMask = 393279
    )
    
    Write-Host "`n=== Добавление прав для $GroupName ===" -ForegroundColor Cyan
    
    # Получаем текущий дескриптор
    $current = Get-WMISecurityDescriptor -Namespace $namespace
    $securityObject = $current.SecurityObject
    $descriptor = $current.Descriptor
    
    Write-Host "Текущий дескриптор получен. Количество ACE: $($descriptor.DACL.Count)" -ForegroundColor Gray
    
    # Удаляем все существующие ACE для этой группы
    $oldCount = $descriptor.DACL.Count
    $newDACL = New-Object System.Collections.ArrayList
    
    foreach ($ace in $descriptor.DACL) {
        if ($ace.Trustee.SIDString -ne $SIDInfo.String) {
            $null = $newDACL.Add($ace)
        } else {
            Write-Host "  Удалена старая ACE для SID: $($SIDInfo.String)" -ForegroundColor Yellow
        }
    }
    
    $removedCount = $oldCount - $newDACL.Count
    if ($removedCount -gt 0) {
        Write-Host "  Удалено ACE: $removedCount" -ForegroundColor Yellow
    }
    
    # Создаем новую ACE
    try {
        # Создаем объект Win32_Trustee
        $trustee = ([WMIClass] "Win32_Trustee").CreateInstance()
        $trustee.SID = $SIDInfo.Binary  # Используем бинарный SID
        $trustee.Name = $GroupName
        
        # Создаем объект Win32_ACE
        $ace = ([WMIClass] "Win32_ACE").CreateInstance()
        $ace.AccessMask = $AccessMask
        $ace.AceFlags = 2  # CI - Container Inherit
        $ace.AceType = 0   # ACCESS_ALLOWED_ACE_TYPE
        $ace.Trustee = $trustee
        
        $null = $newDACL.Add($ace)
        Write-Host "  Добавлена новая ACE с AccessMask: $AccessMask" -ForegroundColor Green
        
    } catch {
        Write-Error "  Ошибка создания ACE: $($_.Exception.Message)"
        return $false
    }
    
    # Обновляем дескриптор
    $descriptor.DACL = $newDACL.ToArray()
    
    # Устанавливаем флаг защиты DACL, чтобы предотвратить наследование
    $descriptor.ControlFlags = $descriptor.ControlFlags -bor 0x8000  # SE_DACL_PROTECTED
    
    Write-Host "  Применяем изменения..." -ForegroundColor Yellow
    
    # Применяем изменения
    $returnCode = Set-WMISecurityDescriptor -SecurityObject $securityObject -Descriptor $descriptor
    
    if ($returnCode -eq 0) {
        Write-Host "  ✓ Права успешно добавлены" -ForegroundColor Green
        Start-Sleep -Seconds 2
        return $true
    } else {
        Write-Error "  ✗ Ошибка добавления прав. Код: $returnCode"
        return $false
    }
}

# Альтернативный метод через SDDL если прямой метод не работает
function Add-WMIPermissionViaSDDL {
    param(
        [string]$GroupName,
        [hashtable]$SIDInfo,
        [int]$AccessMask = 393279
    )
    
    Write-Host "`n=== Альтернативный метод (через SDDL) для $GroupName ===" -ForegroundColor Cyan
    
    # Получаем текущий SDDL
    $sd = Get-WmiObject -Namespace $namespace -Class __SystemSecurity
    $binarySD = @($null)
    $getSDResult = $sd.PsBase.InvokeMethod('GetSD', $binarySD)
    
    if ($getSDResult -ne 0) {
        Write-Error "Не удалось получить бинарный дескриптор"
        return $false
    }
    
    $converter = New-Object System.Management.ManagementClass Win32_SecurityDescriptorHelper
    $sddlObject = $converter.BinarySDToSDDL($binarySD[0])
    $currentSDDL = $sddlObject.SDDL -replace "`r|`n|\s+", ""
    
    Write-Host "Текущий SDDL: $currentSDDL" -ForegroundColor Gray
    
    # Удаляем старые ACE для этого SID
    $pattern = "\([^)]*;;;$([regex]::Escape($SIDInfo.String))\)"
    $cleanedSDDL = $currentSDDL -replace $pattern, ""
    $cleanedSDDL = $cleanedSDDL -replace '\(\)', ''
    
    # Добавляем новую ACE
    $newACE = "(A;CI;CCSWWP;;;$($SIDInfo.String))"
    
    # Вставляем перед последней скобкой
    if ($cleanedSDDL -match '\)$') {
        $newSDDL = $cleanedSDDL.Substring(0, $cleanedSDDL.Length - 1) + $newACE + ")"
    } else {
        $newSDDL = $cleanedSDDL + $newACE
    }
    
    $newSDDL = $newSDDL -replace '\)\(', ')('
    
    Write-Host "Новый SDDL: $newSDDL" -ForegroundColor Gray
    
    # Применяем
    try {
        $binarySDNew = $converter.SDDLToBinarySD($newSDDL)
        $setMethod = $sd.PSBase.GetMethodParameters("SetSD")
        $setMethod.SD = $binarySDNew.BinarySD
        $setResult = $sd.PSBase.InvokeMethod("SetSD", $setMethod, $null)
        
        if ($setResult.ReturnValue -eq 0) {
            Write-Host "  ✓ Права успешно добавлены через SDDL" -ForegroundColor Green
            Start-Sleep -Seconds 2
            return $true
        } else {
            Write-Error "  ✗ Ошибка установки через SDDL. Код: $($setResult.ReturnValue)"
            return $false
        }
    } catch {
        Write-Error "  ✗ Ошибка при установке через SDDL: $($_.Exception.Message)"
        return $false
    }
}

# Основной блок
try {
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║     Настройка прав WMI для групп (рабочая версия)       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Пространство имен: $namespace" -ForegroundColor Yellow
    Write-Host ""
    
    # Проверяем права администратора
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Warning "Скрипт не запущен от имени администратора! Некоторые операции могут не работать."
        Write-Host ""
    }
    
    # Получаем SID для всех групп
    $groupSIDs = @{}
    Write-Host "Получение SID для групп:" -ForegroundColor Cyan
    foreach ($group in $groups) {
        $sidInfo = Get-GroupSID -GroupName $group
        if ($sidInfo) {
            $groupSIDs[$group] = $sidInfo
            Write-Host "  ✓ $group -> $($sidInfo.String)" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $group -> НЕ НАЙДЕНА!" -ForegroundColor Red
        }
    }
    
    if ($groupSIDs.Count -eq 0) {
        throw "Не найдено ни одной группы!"
    }
    
    Write-Host ""
    Write-Host "Начинаем настройку прав..." -ForegroundColor Cyan
    
    # Добавляем права для каждой группы
    $successCount = 0
    $results = @{}
    
    foreach ($group in $groupSIDs.Keys) {
        $sidInfo = $groupSIDs[$group]
        
        # Сначала пробуем прямой метод
        $result = Add-WMIPermission -GroupName $group -SIDInfo $sidInfo -AccessMask $fullAccessMask
        
        # Если прямой метод не сработал, пробуем через SDDL
        if (-not $result) {
            Write-Host "  Прямой метод не сработал, пробуем через SDDL..." -ForegroundColor Yellow
            $result = Add-WMIPermissionViaSDDL -GroupName $group -SIDInfo $sidInfo -AccessMask $fullAccessMask
        }
        
        $results[$group] = $result
        if ($result) { $successCount++ }
    }
    
    # Финальная проверка
    Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                  ФИНАЛЬНАЯ ПРОВЕРКА                       ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    
    $final = Get-WMISecurityDescriptor -Namespace $namespace
    $finalDescriptor = $final.Descriptor
    
    Write-Host "`nТекущие права доступа:" -ForegroundColor Green
    Write-Host ("=" * 80) -ForegroundColor Gray
    
    $aclResults = @()
    foreach ($ace in $finalDescriptor.DACL) {
        $groupName = $null
        $sidString = $ace.Trustee.SIDString
        
        try {
            $sidObj = New-Object System.Security.Principal.SecurityIdentifier($sidString)
            $groupName = $sidObj.Translate([System.Security.Principal.NTAccount]).Value
        } catch {
            $groupName = $ace.Trustee.Name
            if (-not $groupName) { $groupName = $sidString }
        }
        
        $aclResults += [PSCustomObject]@{
            GroupName = $groupName
            AccessMask = $ace.AccessMask
            SID = $sidString
            AceFlags = $ace.AceFlags
        }
    }
    
    $aclResults | Sort-Object GroupName | Format-Table -AutoSize
    
    # Проверяем наши группы
    Write-Host "`n╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                  РЕЗУЛЬТАТЫ ПО ГРУППАМ                    ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    $allSuccess = $true
    foreach ($group in $groupSIDs.Keys) {
        $sidInfo = $groupSIDs[$group]
        $found = $aclResults | Where-Object { $_.SID -eq $sidInfo.String }
        
        if ($found) {
            $mask = $found.AccessMask
            if ($mask -eq $fullAccessMask) {
                Write-Host "  ✓ $group" -ForegroundColor Green
                Write-Host "    SID: $($sidInfo.String)" -ForegroundColor Gray
                Write-Host "    AccessMask: $mask (ПРАВИЛЬНО)" -ForegroundColor Green
            } else {
                Write-Host "  ⚠ $group" -ForegroundColor Yellow
                Write-Host "    SID: $($sidInfo.String)" -ForegroundColor Gray
                Write-Host "    AccessMask: $mask (ожидалось: $fullAccessMask)" -ForegroundColor Yellow
                $allSuccess = $false
            }
        } else {
            Write-Host "  ✗ $group - НЕ НАЙДЕНА В ACL!" -ForegroundColor Red
            Write-Host "    SID: $($sidInfo.String)" -ForegroundColor Gray
            $allSuccess = $false
        }
        Write-Host ""
    }
    
    # Итоговая статистика
    Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                    ИТОГОВАЯ СТАТИСТИКА                   ║" -ForegroundColor Cyan
    Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Всего групп: $($groupSIDs.Count)" -ForegroundColor Yellow
    Write-Host "Успешно настроено: $successCount" -ForegroundColor $(if ($successCount -eq $groupSIDs.Count) { "Green" } else { "Yellow" })
    Write-Host "Требуют внимания: $($groupSIDs.Count - $successCount)" -ForegroundColor $(if ($groupSIDs.Count - $successCount -eq 0) { "Green" } else { "Red" })
    
    if ($allSuccess) {
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║     ✓ ВСЕ ГРУППЫ УСПЕШНО НАСТРОЕНЫ!                    ║" -ForegroundColor Green
        Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Yellow
        Write-Host "║  ⚠ НЕКОТОРЫЕ ГРУППЫ ТРЕБУЮТ РУЧНОЙ НАСТРОЙКИ          ║" -ForegroundColor Yellow
        Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Инструкция по ручной настройке через wbemtest:" -ForegroundColor Cyan
        Write-Host "1. Запустите wbemtest от имени администратора" -ForegroundColor White
        Write-Host "2. Нажмите 'Connect' и введите: root\cimv2" -ForegroundColor White
        Write-Host "3. Нажмите 'Open Instance' и введите: __SystemSecurity=@" -ForegroundColor White
        Write-Host "4. Нажмите 'Methods', выберите 'GetSecurityDescriptor'" -ForegroundColor White
        Write-Host "5. В открывшемся окне нажмите 'Edit', затем 'Add'" -ForegroundColor White
        Write-Host "6. Для каждой группы добавьте ACE с параметрами:" -ForegroundColor White
        Write-Host "   - AccessMask: $fullAccessMask" -ForegroundColor Gray
        Write-Host "   - AceFlags: 2 (Container Inherit)" -ForegroundColor Gray
        Write-Host "   - AceType: 0 (Access Allowed)" -ForegroundColor Gray
        Write-Host "   - Trustee: SID группы" -ForegroundColor Gray
        Write-Host ""
        Write-Host "SID групп для добавления:" -ForegroundColor Cyan
        foreach ($group in $groupSIDs.Keys) {
            Write-Host "  $group : $($groupSIDs[$group].String)" -ForegroundColor White
        }
    }
    
} catch {
    Write-Error "Критическая ошибка: $($_.Exception.Message)"
    Write-Error "Стек вызова: $($_.ScriptStackTrace)"
    
    Write-Host "`nРекомендации:" -ForegroundColor Yellow
    Write-Host "1. Запустите PowerShell от имени администратора" -ForegroundColor White
    Write-Host "2. Проверьте службу WMI: Get-Service winmgmt | Start-Service" -ForegroundColor White
    Write-Host "3. Используйте wmimgmt.msc для проверки настроек безопасности" -ForegroundColor White
}