# BitLocker Management Scripts

[English](#english) | [Русский](#русский) | [Français](#français)

## English

### Description
A set of scripts for managing BitLocker encryption in enterprise environments:
1. PowerShell script for disabling BitLocker encryption on all drives
2. Batch script for importing BitLocker Group Policy settings

### Components

#### Disable-BitLocker.ps1
- Automatically disables BitLocker on all encrypted drives
- Supports multiple languages (English, Russian, French)
- Creates detailed logs in CSV format
- Monitors decryption progress
- Safe for concurrent execution from multiple computers
- Automatically creates scheduled task for monitoring if needed
- Updates final status to COMPLETED when all volumes are decrypted

##### Usage
```powershell
# Run with system language
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1

# Specify language (en-US, ru-RU, fr-FR)
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1 -Culture fr-FR
```

##### Log Location
Logs are stored in: `\\SP63210003\Dist\Bitlocker\BitlockerLog\BitLocker_Status.csv`

#### Import-BitLockerGPO.bat
- Imports BitLocker-related Group Policy settings
- Configures default encryption settings
- Sets up backup policies for recovery keys

##### Usage
```batch
Import-BitLockerGPO.bat
```

### Requirements
- Windows 10/11 or Windows Server 2016+
- PowerShell 5.1 or higher
- Administrative privileges
- Network access to shared folder (\\SP63210003\Dist\Bitlocker)

## Русский

### Описание
Набор скриптов для управления шифрованием BitLocker в корпоративной среде:
1. PowerShell скрипт для отключения шифрования BitLocker на всех дисках
2. Пакетный файл для импорта настроек групповой политики BitLocker

### Компоненты

#### Disable-BitLocker.ps1
- Автоматически отключает BitLocker на всех зашифрованных дисках
- Поддерживает несколько языков (английский, русский, французский)
- Создает подробные логи в формате CSV
- Отслеживает прогресс расшифровки
- Безопасное выполнение с нескольких компьютеров одновременно
- Автоматически создает задачу мониторинга при необходимости
- Обновляет финальный статус на COMPLETED после расшифровки всех томов

##### Использование
```powershell
# Запуск с системным языком
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1

# Указание языка (en-US, ru-RU, fr-FR)
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1 -Culture ru-RU
```

##### Расположение логов
Логи сохраняются в: `\\SP63210003\Dist\Bitlocker\BitlockerLog\BitLocker_Status.csv`

#### Import-BitLockerGPO.bat
- Импортирует настройки групповой политики BitLocker
- Настраивает параметры шифрования по умолчанию
- Устанавливает политики резервного копирования ключей восстановления

##### Использование
```batch
Import-BitLockerGPO.bat
```

### Требования
- Windows 10/11 или Windows Server 2016+
- PowerShell 5.1 или выше
- Права администратора
- Доступ к сетевой папке (\\SP63210003\Dist\Bitlocker)

## Français

### Description
Ensemble de scripts pour la gestion du chiffrement BitLocker dans un environnement d'entreprise :
1. Script PowerShell pour désactiver le chiffrement BitLocker sur tous les lecteurs
2. Script batch pour importer les paramètres de stratégie de groupe BitLocker

### Composants

#### Disable-BitLocker.ps1
- Désactive automatiquement BitLocker sur tous les lecteurs chiffrés
- Prend en charge plusieurs langues (anglais, russe, français)
- Crée des journaux détaillés au format CSV
- Surveille la progression du déchiffrement
- Exécution sécurisée depuis plusieurs ordinateurs simultanément
- Crée automatiquement une tâche de surveillance si nécessaire
- Met à jour le statut final à COMPLETED une fois tous les volumes déchiffrés

##### Utilisation
```powershell
# Exécuter avec la langue système
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1

# Spécifier la langue (en-US, ru-RU, fr-FR)
powershell -ExecutionPolicy Bypass -File Disable-BitLocker.ps1 -Culture fr-FR
```

##### Emplacement des journaux
Les journaux sont stockés dans : `\\SP63210003\Dist\Bitlocker\BitlockerLog\BitLocker_Status.csv`

#### Import-BitLockerGPO.bat
- Importe les paramètres de stratégie de groupe BitLocker
- Configure les paramètres de chiffrement par défaut
- Configure les politiques de sauvegarde des clés de récupération

##### Utilisation
```batch
Import-BitLockerGPO.bat
```

### Prérequis
- Windows 10/11 ou Windows Server 2016+
- PowerShell 5.1 ou supérieur
- Privilèges administratifs
- Accès au dossier partagé (\\SP63210003\Dist\Bitlocker) 