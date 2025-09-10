# System Backup Script
# Created: $(Get-Date)

param(
    [string]$BackupPath = "..\backups"
)

$ErrorActionPreference = "Stop"

# Get timestamp
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $BackupPath $timestamp

Write-Host "Starting system backup..." -ForegroundColor Green
Write-Host "Backup directory: $backupDir" -ForegroundColor Yellow

try {
    # Create backup directory
    if (!(Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }

    # 1. Backup code files
    Write-Host "Backing up code files..." -ForegroundColor Cyan
    $codeBackupDir = Join-Path $backupDir "code"
    New-Item -ItemType Directory -Path $codeBackupDir -Force | Out-Null
    
    # Use robocopy for efficient copying
    & robocopy .. $codeBackupDir /E /R:3 /W:1 /MT:8 /XD venv_new __pycache__ .git node_modules temp tmp /XF *.pyc *.pyo *.log /NFL /NDL /NP
    
    if ($LASTEXITCODE -le 7) {
        Write-Host "Code backup completed" -ForegroundColor Green
    } else {
        throw "Code backup failed with exit code: $LASTEXITCODE"
    }

    # 2. Backup database
    Write-Host "Backing up database..." -ForegroundColor Cyan
    $dbBackupDir = Join-Path $backupDir "database"
    New-Item -ItemType Directory -Path $dbBackupDir -Force | Out-Null
    
    if (Test-Path "..\management.db") {
        Copy-Item "..\management.db" (Join-Path $dbBackupDir "management.db") -Force
        Write-Host "Database backup completed" -ForegroundColor Green
    } else {
        Write-Host "Warning: Database file not found" -ForegroundColor Yellow
    }

    # 3. Backup configuration files
    Write-Host "Backing up configuration files..." -ForegroundColor Cyan
    $configBackupDir = Join-Path $backupDir "config"
    New-Item -ItemType Directory -Path $configBackupDir -Force | Out-Null
    
    $configFiles = @("../.env", "../backend/config.py", "../backend/requirements.txt", "../README.md")
    $configFileNames = @(".env", "config.py", "requirements.txt", "README.md")
    
    for ($i = 0; $i -lt $configFiles.Length; $i++) {
        if (Test-Path $configFiles[$i]) {
            Copy-Item $configFiles[$i] (Join-Path $configBackupDir $configFileNames[$i]) -Force
        }
    }
    Write-Host "Configuration files backup completed" -ForegroundColor Green

    # 4. Backup Git information
    Write-Host "Backing up Git information..." -ForegroundColor Cyan
    $gitBackupDir = Join-Path $backupDir "git-info"
    New-Item -ItemType Directory -Path $gitBackupDir -Force | Out-Null
    
    git branch > (Join-Path $gitBackupDir "branches.txt")
    git log --oneline -10 > (Join-Path $gitBackupDir "recent-commits.txt")
    git status > (Join-Path $gitBackupDir "status.txt")
    git remote -v > (Join-Path $gitBackupDir "remotes.txt")
    
    Write-Host "Git information backup completed" -ForegroundColor Green

    # 5. Create backup manifest
    Write-Host "Creating backup manifest..." -ForegroundColor Cyan
    $manifestContent = "System Backup Manifest`n"
    $manifestContent += "Backup Time: $(Get-Date)`n"
    $manifestContent += "Backup Directory: $backupDir`n`n"
    $manifestContent += "Backup Contents:`n"
    $manifestContent += "- Code files (excluding virtual environment and cache)`n"
    $manifestContent += "- Database file (management.db)`n"
    $manifestContent += "- Configuration files (.env, config.py, requirements.txt)`n"
    $manifestContent += "- Git information (branches, commit history, status)`n`n"
    
    $backupSize = Get-ChildItem $backupDir -Recurse | Measure-Object -Property Length -Sum
    $sizeInMB = [math]::Round($backupSize.Sum/1MB, 2)
    $manifestContent += "Backup Size: $sizeInMB MB`n`n"
    
    $manifestContent += "Restore Instructions:`n"
    $manifestContent += "1. Copy code directory contents to new project directory`n"
    $manifestContent += "2. Restore database file to project root directory`n"
    $manifestContent += "3. Restore configuration files and check environment variables`n"
    $manifestContent += "4. Recreate virtual environment: python -m venv venv_new`n"
    $manifestContent += "5. Install dependencies: pip install -r requirements.txt`n"
    
    $manifestContent | Out-File (Join-Path $backupDir "backup-manifest.txt") -Encoding UTF8
    
    Write-Host "Backup manifest created" -ForegroundColor Green
    
    # 6. Compress backup
    Write-Host "Compressing backup..." -ForegroundColor Cyan
    $zipPath = "$backupDir.zip"
    Compress-Archive -Path $backupDir -DestinationPath $zipPath -Force
    
    if (Test-Path $zipPath) {
        $zipSize = [math]::Round((Get-Item $zipPath).Length/1MB, 2)
        Write-Host "Backup compressed: $zipPath ($zipSize MB)" -ForegroundColor Green
    }
    
    Write-Host "`n=== Backup Completed ===" -ForegroundColor Green
    Write-Host "Backup Location: $backupDir" -ForegroundColor Yellow
    Write-Host "Compressed File: $zipPath" -ForegroundColor Yellow
    Write-Host "Please keep backup files safe" -ForegroundColor Yellow
    
} catch {
    Write-Host "Error during backup: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}