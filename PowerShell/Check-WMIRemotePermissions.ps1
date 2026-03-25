# Test-WMIRemote.ps1
# Скрипт для диагностики удаленного подключения WMI

param(
    [Parameter(Mandatory=$true)]
    [string]$ComputerName,
    
    [PSCredential]$Credential = $null
)

$ErrorActionPreference = "Continue"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║         ДИАГНОСТИКА УДАЛЕННОГО ПОДКЛЮЧЕНИЯ WMI               ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Целевой компьютер: $ComputerName" -ForegroundColor Yellow
Write-Host ""

# 1. Проверка доступности по сети
Write-Host "1. Проверка сетевой доступности:" -ForegroundColor Cyan
$ping = Test-Connection -ComputerName $ComputerName -Count 2 -Quiet
if ($ping) {
    Write-Host "   ✓ Компьютер доступен по сети" -ForegroundColor Green
} else {
    Write-Host "   ✗ Компьютер НЕ ДОСТУПЕН по сети" -ForegroundColor Red
    Write-Host "     Проверьте: подключение к сети, брандмауэр, имя компьютера" -ForegroundColor Yellow
}
Write-Host ""

# 2. Проверка портов
Write-Host "2. Проверка необходимых портов:" -ForegroundColor Cyan
$ports = @{
    135 = "RPC Endpoint Mapper"
    445 = "SMB"
    139 = "NetBIOS"
}

foreach ($port in $ports.Keys | Sort-Object) {
    try {
        $tcp = New-Object System.Net.Sockets.TcpClient
        $connect = $tcp.BeginConnect($ComputerName, $port, $null, $null)
        $wait = $connect.AsyncWaitHandle.WaitOne(1000, $false)
        if ($wait) {
            $tcp.EndConnect($connect)
            Write-Host "   ✓ Порт $port ($($ports[$port])): ДОСТУПЕН" -ForegroundColor Green
            $tcp.Close()
        } else {
            Write-Host "   ✗ Порт $port ($($ports[$port])): НЕ ДОСТУПЕН" -ForegroundColor Red
        }
    } catch {
        Write-Host "   ✗ Порт $port ($($ports[$port])): ОШИБКА - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# 3. Проверка служб на удаленном компьютере
Write-Host "3. Проверка служб:" -ForegroundColor Cyan

$services = @{
    "WinRM" = "Windows Remote Management"
    "RpcSs" = "Remote Procedure Call (RPC)"
    "Winmgmt" = "Windows Management Instrumentation"
}

foreach ($service in $services.Keys) {
    try {
        $svc = Get-Service -ComputerName $ComputerName -Name $service -ErrorAction Stop
        Write-Host "   ✓ $service ($($services[$service])): $($svc.Status)" -ForegroundColor Green
    } catch {
        Write-Host "   ✗ $service ($($services[$service])): НЕДОСТУПЕН - $($_.Exception.Message)" -ForegroundColor Red
    }
}
Write-Host ""

# 4. Проверка брандмауэра через удаленный реестр (если доступен)
Write-Host "4. Проверка правил брандмауэра:" -ForegroundColor Cyan
try {
    $reg = [Microsoft.Win32.RegistryKey]::OpenRemoteBaseKey('LocalMachine', $ComputerName)
    $fwKey = $reg.OpenSubKey("SYSTEM\CurrentControlSet\Services\SharedAccess\Parameters\FirewallPolicy\DomainProfile")
    if ($fwKey) {
        Write-Host "   ✓ Доступ к настройкам брандмауэра получен" -ForegroundColor Green
        $enableFirewall = $fwKey.GetValue("EnableFirewall")
        if ($enableFirewall -eq 1) {
            Write-Host "   ⚠ Брандмауэр включен. Необходимо разрешить WMI" -ForegroundColor Yellow
        } else {
            Write-Host "   ✓ Брандмауэр отключен" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "   ✗ Не удалось проверить брандмауэр: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 5. Попытка WMI подключения с разными параметрами
Write-Host "5. Тестирование WMI подключения:" -ForegroundColor Cyan

# Попытка 1: Стандартное подключение
try {
    $wmi = Get-WmiObject -ComputerName $ComputerName -Class Win32_ComputerSystem -ErrorAction Stop
    Write-Host "   ✓ Стандартное подключение: УСПЕШНО" -ForegroundColor Green
    Write-Host "     Компьютер: $($wmi.Name)" -ForegroundColor Gray
    Write-Host "     Домен: $($wmi.Domain)" -ForegroundColor Gray
} catch {
    Write-Host "   ✗ Стандартное подключение: $($_.Exception.Message)" -ForegroundColor Red
}

# Попытка 2: С указанием аутентификации
try {
    $options = New-Object System.Management.ConnectionOptions
    $options.Authentication = 6  # PacketPrivacy
    $options.Impersonation = 3    # Impersonate
    $options.EnablePrivileges = $true
    
    if ($Credential) {
        $options.Username = $Credential.UserName
        $options.Password = $Credential.GetNetworkCredential().Password
    }
    
    $scope = New-Object System.Management.ManagementScope("\\$ComputerName\root\cimv2", $options)
    $scope.Connect()
    Write-Host "   ✓ Подключение с PacketPrivacy: УСПЕШНО" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Подключение с PacketPrivacy: $($_.Exception.Message)" -ForegroundColor Red
}

# Попытка 3: Через DCOM (альтернативный метод)
try {
    $wmi = Get-WmiObject -ComputerName $ComputerName -Class Win32_ComputerSystem -Authentication PacketPrivacy -Impersonation Impersonate -ErrorAction Stop
    Write-Host "   ✓ Подключение через DCOM: УСПЕШНО" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Подключение через DCOM: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 6. Проверка локальной политики безопасности
Write-Host "6. Проверка настроек безопасности:" -ForegroundColor Cyan
try {
    $wmi = Get-WmiObject -ComputerName $ComputerName -Class Win32_UserAccount -Filter "Name='Administrator'" -ErrorAction Stop
    Write-Host "   ✓ Доступ к учетным записям получен" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Доступ к учетным записям: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Итоговые рекомендации
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    РЕКОМЕНДАЦИИ                                 ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "На целевом компьютере ($ComputerName) выполните следующие команды (от имени администратора):" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Включите и настройте службы:" -ForegroundColor White
Write-Host "   Set-Service WinRM -StartupType Automatic" -ForegroundColor Gray
Write-Host "   Start-Service WinRM" -ForegroundColor Gray
Write-Host "   Set-Service Winmgmt -StartupType Automatic" -ForegroundColor Gray
Write-Host "   Start-Service Winmgmt" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Настройте брандмауэр для WMI:" -ForegroundColor White
Write-Host "   netsh advfirewall firewall set rule group=\"Windows Management Instrumentation (WMI)\" new enable=yes" -ForegroundColor Gray
Write-Host "   # Или добавить правило вручную:" -ForegroundColor Gray
Write-Host "   netsh advfirewall firewall add rule name=\"WMI\" dir=in action=allow protocol=TCP localport=135" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Настройте DCOM разрешения:" -ForegroundColor White
Write-Host "   dcomcnfg -> Component Services -> Computers -> My Computer -> Properties" -ForegroundColor Gray
Write-Host "   -> COM Security -> Access Permissions -> Edit Limits -> Добавить нужных пользователей" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Настройте WMI разрешения:" -ForegroundColor White
Write-Host "   wmimgmt.msc -> WMI Control -> Properties -> Security -> root -> Security" -ForegroundColor Gray
Write-Host "   -> Добавить нужных пользователей с правами" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Проверьте UAC и политики:" -ForegroundColor White
Write-Host "   # Отключите фильтрацию UAC для удаленного доступа" -ForegroundColor Gray
Write-Host "   reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f" -ForegroundColor Gray
Write-Host "   # Или через групповую политику:" -ForegroundColor Gray
Write-Host "   gpedit.msc -> Computer Config -> Admin Templates -> Network -> Network Access" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Перезапустите службу WMI после изменений:" -ForegroundColor White
Write-Host "   net stop winmgmt && net start winmgmt" -ForegroundColor Gray