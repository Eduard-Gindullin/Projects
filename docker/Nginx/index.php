<?php

$headers = apache_request_headers();

// Указываем заголовки, которые мы хотим вывести
$includeHeaders = [
    'X-Real-IP',
    'X-Forwarded-For'
];

foreach ($headers as $header => $value) {
    // Проверяем, находится ли текущий заголовок в списке разрешенных для вывода
    if (in_array($header, $includeHeaders)) {
        echo htmlspecialchars($header) . ": " . htmlspecialchars($value) . "\n";
    }
}

?>