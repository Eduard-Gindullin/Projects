<#
.SYNOPSIS
    Скрипт для проверки компьютеров в домене GSB на соответствие требованиям Windows 11.
.DESCRIPTION
    Проверяет компьютеры в указанных подразделениях AD на соответствие минимальным требованиям Windows 11:
    - Поддерживаемый процессор (из списка Intel)
    - 64-битный процессор с 2+ ядрами и 1 ГГц тактовой частотой
    - 4 ГБ+ ОЗУ
    - 64 ГБ+ хранилища
    - TPM версия 2.0
    - Поддержка Secure Boot
    - DirectX 12 / WDDM 2.x
.NOTES
    Требуется:
    - Модуль ActiveDirectory
    - Права администратора домена
    - Доступ к WMI на проверяемых компьютерах
    - PowerShell 5.1 или новее
#>

# Импортируем модуль ActiveDirectory
Import-Module ActiveDirectory -ErrorAction Stop

# Параметры скрипта
$Domain = "GSB"
$OUs = @(
    "OU=Computers,OU=BMK,OU=RU-BELEBEY,OU=EMEA,DC=$Domain,DC=local",
    "OU=Computers,OU=BEV,OU=RU-MOSCOW,OU=EMEA,DC=$Domain,DC=local",
    "OU=Computers,OU=AGRO-2000,OU=RU-UFA,OU=EMEA,DC=$Domain,DC=local"
)

$DaysInactive = 90 # Пропускать компьютеры, не активные более этого количества дней
$OutputFile = "Win11_Compatibility_Report_$(Get-Date -Format 'yyyyMMdd').csv"

# Список поддерживаемых процессоров для Windows 11 (из файла)
$SupportedProcessors = @(
    "Intel® Atom® x6200FE",
    "Intel® Atom® x6211E",
    "Intel® Atom® x6212RE",
    "Intel® Atom® x6413E",
    "Intel® Atom® x6414RE",
    "Intel® Atom® x6425E",
    "Intel® Atom® x6425RE",
    "Intel® Atom® x6427FE",
    "Intel® Celeron® 6305",
    "Intel® Celeron® 7300",
    "Intel® Celeron® 7305",
    "Intel® Celeron® 3867U",
    "Intel® Celeron® 4205U",
    "Intel® Celeron® 4305U",
    "Intel® Celeron® 4305UE",
    "Intel® Celeron® 5205U",
    "Intel® Celeron® 5305U"
    # Добавьте остальные процессоры из файла при необходимости
)

# Функция для проверки поддержки процессора Windows 11
function Test-Win11Processor {
    param (
        [string]$ProcessorName
    )
    
    # Нормализуем имя процессора для сравнения
    $Normalized = $ProcessorName -replace "\(R\)|®|™|\(TM\)" -replace "\s+", " " -replace "^\s+|\s+$" -replace "CPU|@.*"
    
    foreach ($proc in $SupportedProcessors) {
        $NormalizedProc = $proc -replace "\(R\)|®|™|\(TM\)" -replace "\s+", " " -replace "^\s+|\s+$"
        if ($Normalized -like "*$NormalizedProc*") {
            return $true
        }
    }
    
    return $false
}

# Функция для проверки одного компьютера
function Test-Win11Compatibility {
    param (
        [string]$ComputerName
    )

    # Инициализируем объект результата
    $Result = [PSCustomObject]@{
        ComputerName          = $ComputerName
        OSVersion            = $null
        ProcessorName        = $null
        ProcessorCompatible  = $false
        CPUCompatible        = $false
        Cores               = 0
        RAMGB               = 0
        StorageGB           = 0
        TPMVersion          = 0
        SecureBoot          = $false
        GraphicsCompatible  = $false
        LastBootTime       = $null
        IsOnline           = $false
        Error              = $null
    }

    try {
        # Проверяем доступность компьютера
        $Result.IsOnline = Test-Connection -ComputerName $ComputerName -Count 1 -Quiet -ErrorAction Stop

        if (-not $Result.IsOnline) {
            $Result.Error = "Computer is offline"
            return $Result
        }

        # Получаем информацию о системе через WMI
        $OS = Get-WmiObject -Class Win32_OperatingSystem -ComputerName $ComputerName -ErrorAction Stop
        $Processor = Get-WmiObject -Class Win32_Processor -ComputerName $ComputerName -ErrorAction Stop | Select-Object -First 1
        $Memory = Get-WmiObject -Class Win32_PhysicalMemory -ComputerName $ComputerName -ErrorAction Stop | Measure-Object -Property Capacity -Sum
        $Disk = Get-WmiObject -Class Win32_LogicalDisk -ComputerName $ComputerName -Filter "DriveType=3" -ErrorAction Stop | Select-Object -First 1
        $TPM = Get-WmiObject -Class Win32_Tpm -Namespace "root\cimv2\security\microsofttpm" -ComputerName $ComputerName -ErrorAction SilentlyContinue
        $SecureBoot = Get-WmiObject -Class Win32_ComputerSystem -ComputerName $ComputerName -Property "SecureBootState" -ErrorAction SilentlyContinue
        $VideoController = Get-WmiObject -Class Win32_VideoController -ComputerName $ComputerName -ErrorAction SilentlyContinue

        # Заполняем результаты проверок
        $Result.OSVersion = $OS.Caption
        $Result.ProcessorName = $Processor.Name
        $Result.LastBootTime = $OS.ConvertToDateTime($OS.LastBootUpTime)
        
        # Проверка процессора (поддержка Windows 11)
        $Result.ProcessorCompatible = Test-Win11Processor -ProcessorName $Processor.Name
        
        # Проверка процессора (технические характеристики)
        if ($Processor.AddressWidth -eq 64 -and $Processor.NumberOfCores -ge 2 -and $Processor.MaxClockSpeed -ge 1000) {
            $Result.CPUCompatible = $true
            $Result.Cores = $Processor.NumberOfCores
        }

        # Проверка памяти
        if ($Memory.Sum -ge 4GB) {
            $Result.RAMGB = [math]::Round($Memory.Sum / 1GB, 2)
        }

        # Проверка хранилища
        if ($Disk.Size -ge 64GB) {
            $Result.StorageGB = [math]::Round($Disk.Size / 1GB, 2)
        }

        # Проверка TPM
        if ($TPM -and $TPM.SpecVersion -match "2.0") {
            $Result.TPMVersion = 2.0
        } elseif ($TPM) {
            $Result.TPMVersion = 1.2
        }

        # Проверка Secure Boot
        if ($SecureBoot -and $SecureBoot.SecureBootState -eq 1) {
            $Result.SecureBoot = $true
        }

        # Проверка графики
        if ($VideoController -and $VideoController.DriverVersion -match "2\d\.\d+\.\d+") {
            $Result.GraphicsCompatible = $true
        }

    } catch {
        $Result.Error = $_.Exception.Message
    }

    return $Result
}

# Получаем список компьютеров из указанных OU
$Computers = foreach ($OU in $OUs) {
    try {
        Get-ADComputer -Filter * -SearchBase $OU -Properties Name, LastLogonDate, OperatingSystem |
        Where-Object { $_.LastLogonDate -gt (Get-Date).AddDays(-$DaysInactive) -or $_.LastLogonDate -eq $null }
    } catch {
        Write-Warning "Ошибка при получении компьютеров из OU $OU : $_"
    }
}

if (-not $Computers) {
    Write-Host "Не найдено активных компьютеров в указанных OU." -ForegroundColor Yellow
    exit
}

Write-Host "Найдено компьютеров для проверки: $($Computers.Count)" -ForegroundColor Cyan

# Проверяем каждый компьютер
$Results = @()
$Total = $Computers.Count
$Current = 0

foreach ($Computer in $Computers) {
    $Current++
    $Progress = [math]::Round(($Current / $Total) * 100, 2)
    Write-Progress -Activity "Проверка компьютеров на соответствие Windows 11" -Status "$Progress% завершено" -PercentComplete $Progress -CurrentOperation $Computer.Name

    $Result = Test-Win11Compatibility -ComputerName $Computer.Name
    $Results += $Result
}

# Анализируем результаты
$CompatibleCount = ($Results | Where-Object {
    $_.ProcessorCompatible -and 
    $_.CPUCompatible -and 
    $_.RAMGB -ge 4 -and 
    $_.StorageGB -ge 64 -and 
    $_.TPMVersion -ge 2.0 -and 
    $_.SecureBoot -and 
    $_.GraphicsCompatible -and 
    -not $_.Error
}).Count

$IncompatibleCount = $Results.Count - $CompatibleCount

# Формируем финальный отчет
$Report = $Results | Select-Object @{Name="Имя компьютера"; Expression={$_.ComputerName}},
                                  @{Name="ОС"; Expression={$_.OSVersion}},
                                  @{Name="Процессор"; Expression={$_.ProcessorName}},
                                  @{Name="Соответствует Win11"; Expression={
                                      if ($_.ProcessorCompatible -and $_.CPUCompatible -and $_.RAMGB -ge 4 -and $_.StorageGB -ge 64 -and $_.TPMVersion -ge 2.0 -and $_.SecureBoot -and $_.GraphicsCompatible) { "Да" } else { "Нет" }
                                  }},
                                  @{Name="Поддержка процессора"; Expression={if ($_.ProcessorCompatible) { "Да" } else { "Нет" }}},
                                  @{Name="Процессор (64-bit, 2+ ядер)"; Expression={if ($_.CPUCompatible) { "Да" } else { "Нет" }}},
                                  @{Name="Ядер"; Expression={$_.Cores}},
                                  @{Name="ОЗУ (ГБ)"; Expression={$_.RAMGB}},
                                  @{Name="Диск (ГБ)"; Expression={$_.StorageGB}},
                                  @{Name="TPM"; Expression={if ($_.TPMVersion -ge 2) { "2.0" } elseif ($_.TPMVersion -eq 1.2) { "1.2" } else { "Нет" }}},
                                  @{Name="Secure Boot"; Expression={if ($_.SecureBoot) { "Да" } else { "Нет" }}},
                                  @{Name="Графика (DX12/WDDM2.x)"; Expression={if ($_.GraphicsCompatible) { "Да" } else { "Нет" }}},
                                  @{Name="Последняя загрузка"; Expression={$_.LastBootTime}},
                                  @{Name="Онлайн"; Expression={if ($_.IsOnline) { "Да" } else { "Нет" }}},
                                  @{Name="Ошибка"; Expression={$_.Error}}

# Выводим сводку
Write-Host "`nРезультаты проверки:" -ForegroundColor Cyan
Write-Host "Всего компьютеров проверено: $($Results.Count)" -ForegroundColor White
Write-Host "Полностью соответствуют требованиям Windows 11: $CompatibleCount" -ForegroundColor Green
Write-Host "Не соответствуют требованиям Windows 11: $IncompatibleCount" -ForegroundColor Red
Write-Host "Оффлайн или ошибка подключения: $(($Results | Where-Object { -not $_.IsOnline -or $_.Error }).Count)" -ForegroundColor Yellow

# Сохраняем отчет
$Report | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8 -Delimiter ";"
Write-Host "`nОтчет сохранен в файл: $OutputFile" -ForegroundColor Green

# Выводим пример несоответствующих компьютеров
if ($IncompatibleCount -gt 0) {
    Write-Host "`nПримеры несоответствующих компьютеров:" -ForegroundColor Red
    $Report | Where-Object { $_.'Соответствует Win11' -eq "Нет" } | Select-Object -First 5 | Format-Table -AutoSize
}