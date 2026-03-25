# Проверочный скрипт для верификации прав WMI
$namespace = "ROOT\CIMV2"
$groups = @(
    "GDLRU-BELEBEY-BMK-Administrators-Level2",
    "GDLRU-MOSCOW-BEV-Administrators-Level2",
    "GDLRU-DC1-SFD_RUSSIA-Administrators-Level2"
)
$expectedAccessMask = 393279

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║              ПРОВЕРКА ПРАВ WMI ДЛЯ ГРУПП                       ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Пространство имен: $namespace" -ForegroundColor Yellow
Write-Host ""

function Get-GroupSID {
    param([string]$GroupName)
    try {
        $ntAccount = New-Object System.Security.Principal.NTAccount($GroupName)
        $sid = $ntAccount.Translate([System.Security.Principal.SecurityIdentifier])
        return $sid.Value
    } catch {
        return $null
    }
}

function Test-WMIPermission {
    param([string]$GroupName, [string]$SID, [int]$ExpectedMask)
    
    try {
        $sd = Get-WmiObject -Namespace "ROOT\CIMV2" -Class __SystemSecurity
        $method = $sd.PSBase.GetMethodParameters("GetSecurityDescriptor")
        $result = $sd.PSBase.InvokeMethod("GetSecurityDescriptor", $method, $null)
        
        if ($result.ReturnValue -eq 0) {
            $ace = $result.Descriptor.DACL | Where-Object { $_.Trustee.SIDString -eq $SID }
            
            if ($ace) {
                $actualMask = $ace.AccessMask
                if ($actualMask -eq $ExpectedMask) {
                    return @{Success = $true; ActualMask = $actualMask; Message = "ПРАВИЛЬНО"}
                } else {
                    return @{Success = $false; ActualMask = $actualMask; Message = "AccessMask = $actualMask (ожидалось: $ExpectedMask)"}
                }
            } else {
                return @{Success = $false; ActualMask = $null; Message = "ACE не найден"}
            }
        } else {
            return @{Success = $false; ActualMask = $null; Message = "Ошибка получения дескриптора: $($result.ReturnValue)"}
        }
    } catch {
        return @{Success = $false; ActualMask = $null; Message = "Ошибка: $($_.Exception.Message)"}
    }
}

# Получаем SID групп
$groupSIDs = @{}
Write-Host "Получение SID групп:" -ForegroundColor Cyan
foreach ($group in $groups) {
    $sid = Get-GroupSID -GroupName $group
    if ($sid) {
        $groupSIDs[$group] = $sid
        Write-Host "  ✓ $group -> $sid" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $group -> НЕ НАЙДЕНА!" -ForegroundColor Red
    }
}
Write-Host ""

# Проверяем права для каждой группы
Write-Host "Проверка прав доступа:" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

$allSuccess = $true
$results = @{}

foreach ($group in $groupSIDs.Keys) {
    $sid = $groupSIDs[$group]
    Write-Host "`nГруппа: $group" -ForegroundColor Yellow
    Write-Host "  SID: $sid" -ForegroundColor Gray
    
    $test = Test-WMIPermission -GroupName $group -SID $sid -ExpectedMask $expectedAccessMask
    
    if ($test.Success) {
        Write-Host "  Статус: ✓ $($test.Message)" -ForegroundColor Green
        Write-Host "  AccessMask: $($test.ActualMask)" -ForegroundColor Green
        $results[$group] = $true
    } else {
        Write-Host "  Статус: ✗ $($test.Message)" -ForegroundColor Red
        if ($test.ActualMask) {
            Write-Host "  Текущий AccessMask: $($test.ActualMask)" -ForegroundColor Red
        }
        $results[$group] = $false
        $allSuccess = $false
    }
}

# Получаем полную информацию о всех ACE
Write-Host "`n" + ("=" * 70) -ForegroundColor Gray
Write-Host "`nПолный список ACE в WMI Security Descriptor:" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Gray

try {
    $sd = Get-WmiObject -Namespace "ROOT\CIMV2" -Class __SystemSecurity
    $method = $sd.PSBase.GetMethodParameters("GetSecurityDescriptor")
    $result = $sd.PSBase.InvokeMethod("GetSecurityDescriptor", $method, $null)
    
    if ($result.ReturnValue -eq 0) {
        $aclList = @()
        
        foreach ($ace in $result.Descriptor.DACL) {
            $groupName = $null
            $sidString = $ace.Trustee.SIDString
            
            # Пытаемся получить имя группы по SID
            try {
                $sidObj = New-Object System.Security.Principal.SecurityIdentifier($sidString)
                $groupName = $sidObj.Translate([System.Security.Principal.NTAccount]).Value
            } catch {
                $groupName = $ace.Trustee.Name
                if (-not $groupName) { $groupName = $sidString }
            }
            
            $aclList += [PSCustomObject]@{
                GroupName = $groupName
                SID = $sidString
                AccessMask = $ace.AccessMask
                AceType = $ace.AceType
                AceFlags = $ace.AceFlags
            }
        }
        
        $aclList | Sort-Object GroupName | Format-Table -AutoSize
        
        # Подсчет статистики
        $totalACE = $aclList.Count
        $correctACE = ($aclList | Where-Object { $_.AccessMask -eq $expectedAccessMask }).Count
        
        Write-Host "`nСтатистика ACE:" -ForegroundColor Cyan
        Write-Host "  Всего ACE: $totalACE" -ForegroundColor Yellow
        Write-Host "  ACE с полными правами (AccessMask=$expectedAccessMask): $correctACE" -ForegroundColor Yellow
        Write-Host ""
        
    } else {
        Write-Error "Не удалось получить дескриптор безопасности: $($result.ReturnValue)"
    }
} catch {
    Write-Error "Ошибка при получении дескриптора: $($_.Exception.Message)"
}

# Итоговый вердикт
Write-Host ("=" * 70) -ForegroundColor Gray
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $(if ($allSuccess) { "Green" } else { "Yellow" })
if ($allSuccess) {
    Write-Host "║              ✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!                ║" -ForegroundColor Green
    Write-Host "║          Права WMI корректно настроены для всех групп        ║" -ForegroundColor Green
} else {
    Write-Host "║              ⚠ ОБНАРУЖЕНЫ ПРОБЛЕМЫ С ПРАВАМИ                 ║" -ForegroundColor Yellow
    Write-Host "║          Некоторые группы имеют неправильные права           ║" -ForegroundColor Yellow
}
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $(if ($allSuccess) { "Green" } else { "Yellow" })

if (-not $allSuccess) {
    Write-Host "`nПроблемные группы:" -ForegroundColor Red
    foreach ($group in $results.Keys | Where-Object { -not $results[$_] }) {
        Write-Host "  ✗ $group" -ForegroundColor Red
    }
    
    Write-Host "`nРекомендации:" -ForegroundColor Yellow
    Write-Host "1. Запустите основной скрипт настройки еще раз" -ForegroundColor White
    Write-Host "2. Проверьте, что группы существуют в Active Directory" -ForegroundColor White
    Write-Host "3. Используйте wbemtest для ручной настройки (см. инструкцию)" -ForegroundColor White
    Write-Host "4. Перезапустите службу WMI: Restart-Service winmgmt" -ForegroundColor White
}

Write-Host ""
Write-Host "Проверка завершена в: $(Get-Date -Format 'dd.MM.yyyy HH:mm:ss')" -ForegroundColor Gray