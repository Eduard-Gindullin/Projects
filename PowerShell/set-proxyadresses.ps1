# DN группы, для которой применяем изменения
$groupDN = "CN=MS_E3,OU=SOFTWARE Groups,DC=belmol,DC=loc"

$users = Get-ADUser -Filter {memberOf -eq $groupDN} -Properties proxyAddresses, UserPrincipalName

foreach ($user in $users) {
    if (-not $user.UserPrincipalName) { continue }
    
    $login = $user.UserPrincipalName.Split('@')[0]
    
    # Целевые адреса — гарантированно строки
    $requiredAddresses = @(
        [string]"SMTP:$login@belmol.ru",
        [string]"smtp:$login@belmol.com",
        [string]"smtp:$login@savencia-fd.ru"
    )
    
    # Текущие адреса — преобразуем в массив строк
    $currentAddresses = @($user.proxyAddresses | ForEach-Object { $_.ToString() })
    
    # Находим недостающие адреса (только строки)
    $toAdd = @($requiredAddresses | Where-Object { $_ -notin $currentAddresses } | ForEach-Object { $_.ToString() })
    
    if ($toAdd.Count -gt 0) {
        Set-ADUser -Identity $user.DistinguishedName -Add @{proxyAddresses = $toAdd}
        Write-Host "Добавлены адреса для $($user.UserPrincipalName): $($toAdd -join ', ')"
        # Обновляем список адресов после добавления
        $currentAddresses += $toAdd
    }
    
    # Проверяем, установлен ли правильный основной SMTP
    $primaryExists = ($currentAddresses -match "^SMTP:$login@belmol\.ru$").Count -gt 0
    
    if (-not $primaryExists) {
        # Строим новый массив, исправляя префиксы
        $fixed = @()
        foreach ($addr in $currentAddresses) {
            $s = $addr.ToString()
            if ($s -eq "smtp:$login@belmol.ru") {
                $fixed += "SMTP:$login@belmol.ru"
            }
            elseif ($s -match "^SMTP:.*@belmol\.ru$" -and $s -ne "SMTP:$login@belmol.ru") {
                $fixed += $s -replace "^SMTP:", "smtp:"
            }
            else {
                $fixed += $s
            }
        }
        
        # Убедимся, что все требуемые адреса присутствуют
        foreach ($req in $requiredAddresses) {
            $reqStr = $req.ToString()
            if ($reqStr -notin $fixed) {
                $fixed += $reqStr
            }
        }
        
        # Применяем исправленный массив
        Set-ADUser -Identity $user.DistinguishedName -Replace @{proxyAddresses = $fixed}
        Write-Host "Установлен основной SMTP для $($user.UserPrincipalName): SMTP:$login@belmol.ru"
    }
}