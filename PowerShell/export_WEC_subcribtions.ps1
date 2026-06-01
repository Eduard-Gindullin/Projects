$output = wecutil gr WEC
$csvData = [System.Collections.ArrayList]::new()
$inSources = $false
$currentHost = $null
$indentEventSources = -1

foreach ($line in $output) {
    if (-not $inSources) {
        # Ждём строку "EventSources:"
        if ($line -match '^\s*EventSources:') {
            $inSources = $true
            # Запоминаем отступ этой строки (по количеству пробелов в начале)
            $indentEventSources = ($line -replace '^(\s*).*', '$1').Length
        }
        continue
    }

    # После нахождения секции проверяем, не закончилась ли она
    if ($line.Trim() -eq '') { continue }  # пустые строки пропускаем
    $leadingSpaces = ($line -replace '^(\s*).*', '$1').Length
    if ($leadingSpaces -le $indentEventSources) {
        # Отступ стал меньше или равен отступу заголовка — секция источников кончилась
        break
    }

    # Если строка без двоеточия — это имя хоста
    if ($line -notmatch ':') {
        if ($null -ne $currentHost) {
            $null = $csvData.Add($currentHost)
        }
        $currentHost = [PSCustomObject]@{
            Host              = $line.Trim()
            RunTimeStatus     = ''
            LastError         = ''
            LastHeartbeatTime = ''
        }
    }
    else {
        # Строка с параметром (например "RunTimeStatus: Active")
        if ($line -match '^\s*([^:]+):\s*(.*)') {
            $key   = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($null -ne $currentHost) {
                switch ($key) {
                    'RunTimeStatus'     { $currentHost.RunTimeStatus = $value }
                    'LastError'         { $currentHost.LastError = $value }
                    'LastHeartbeatTime' { $currentHost.LastHeartbeatTime = $value }
                }
            }
        }
    }
}

# Добавляем последний обработанный хост
if ($null -ne $currentHost) {
    $null = $csvData.Add($currentHost)
}

# Экспорт в CSV
$csvData | Export-Csv -Path C:\temp\WEC_EventSources.csv -NoTypeInformation -Encoding UTF8
Write-Host "Файл сохранён: C:\temp\WEC_EventSources.csv"