# BitLocker Disable Tool / Outil de désactivation BitLocker / Инструмент отключения BitLocker

[English](#english) | [Français](#français) | [Русский](#русский)

## English

### Description
A set of scripts to automatically disable BitLocker encryption through Group Policy (GPO).

### Requirements
- Windows 10/11 Pro or Enterprise
- Remote Server Administration Tools (RSAT)
- Administrator rights

### Installation
1. Download all files to a local directory
2. Run PowerShell as Administrator
3. Navigate to the script directory

### Usage
```powershell
# Using system language
.\Disable-BitLocker.ps1

# Specify language explicitly
.\Disable-BitLocker.ps1 -Culture en-US  # English
.\Disable-BitLocker.ps1 -Culture fr-FR  # French
.\Disable-BitLocker.ps1 -Culture ru-RU  # Russian

# Import GPO (uses system language by default)
.\Import-BitLockerGPO.bat

# Import GPO with specific language
.\Import-BitLockerGPO.bat en-US  # English
.\Import-BitLockerGPO.bat fr-FR  # French
.\Import-BitLockerGPO.bat ru-RU  # Russian
```

### Monitoring
- The script creates a scheduled task that monitors decryption progress
- Task runs every 10 minutes
- Automatically removes itself when decryption is complete

### Logs
- `BitLocker_Status.csv` - Decryption progress
- `BitLocker_Disable.log` - Operation log
- `GPO_Import.log` - Policy creation log

## Français

### Description
Un ensemble de scripts pour désactiver automatiquement le chiffrement BitLocker via la Stratégie de Groupe (GPO).

### Prérequis
- Windows 10/11 Pro ou Enterprise
- Outils d'administration de serveur distant (RSAT)
- Droits d'administrateur

### Installation
1. Téléchargez tous les fichiers dans un répertoire local
2. Exécutez PowerShell en tant qu'administrateur
3. Naviguez vers le répertoire des scripts

### Utilisation
```powershell
# Utilisation de la langue système
.\Disable-BitLocker.ps1

# Spécifier la langue explicitement
.\Disable-BitLocker.ps1 -Culture en-US  # Anglais
.\Disable-BitLocker.ps1 -Culture fr-FR  # Français
.\Disable-BitLocker.ps1 -Culture ru-RU  # Russe

# Importer GPO (utilise la langue système par défaut)
.\Import-BitLockerGPO.bat

# Importer GPO avec une langue spécifique
.\Import-BitLockerGPO.bat en-US  # Anglais
.\Import-BitLockerGPO.bat fr-FR  # Français
.\Import-BitLockerGPO.bat ru-RU  # Russe
```

### Surveillance
- Le script crée une tâche planifiée qui surveille la progression du déchiffrement
- La tâche s'exécute toutes les 10 minutes
- Se supprime automatiquement une fois le déchiffrement terminé

### Journaux
- `BitLocker_Status.csv` - Progression du déchiffrement
- `BitLocker_Disable.log` - Journal des opérations
- `GPO_Import.log` - Journal de création de stratégie

## Русский

### Описание
Набор скриптов для автоматического отключения шифрования BitLocker через групповые политики (GPO).

### Требования
- Windows 10/11 Pro или Enterprise
- Remote Server Administration Tools (RSAT)
- Права администратора

### Установка
1. Скачайте все файлы в локальную директорию
2. Запустите PowerShell от имени администратора
3. Перейдите в директорию со скриптами

### Использование
```powershell
# Использование языка системы
.\Disable-BitLocker.ps1

# Явное указание языка
.\Disable-BitLocker.ps1 -Culture en-US  # Английский
.\Disable-BitLocker.ps1 -Culture fr-FR  # Французский
.\Disable-BitLocker.ps1 -Culture ru-RU  # Русский

# Импорт GPO (по умолчанию использует язык системы)
.\Import-BitLockerGPO.bat

# Импорт GPO с указанием языка
.\Import-BitLockerGPO.bat en-US  # Английский
.\Import-BitLockerGPO.bat fr-FR  # Французский
.\Import-BitLockerGPO.bat ru-RU  # Русский
```

### Мониторинг
- Скрипт создает задачу в планировщике для отслеживания прогресса расшифровки
- Задача выполняется каждые 10 минут
- Автоматически удаляется после завершения расшифровки

### Логи
- `BitLocker_Status.csv` - Прогресс расшифровки
- `BitLocker_Disable.log` - Журнал операций
- `GPO_Import.log` - Журнал создания политики 