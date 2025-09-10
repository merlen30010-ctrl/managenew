# System Restore Script
# This script helps restore the system from backup

param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath,
    [string]$RestorePath = "."
)

$ErrorActionPreference = "Stop"

Write-Host "Starting system restore..." -ForegroundColor Green
Write-Host "Backup source: $BackupPath" -ForegroundColor Yellow
Write-Host "Restore target: $RestorePath" -ForegroundColor Yellow

try {
    # Check if backup exists
    if (!(Test-Path $BackupPath)) {
        throw "Backup path not found: $BackupPath"
    }
    
    # If backup is a zip file, extract it first
    if ($BackupPath.EndsWith(".zip")) {
        Write-Host "Extracting backup archive..." -ForegroundColor Cyan
        $extractPath = $BackupPath.Replace(".zip", "")
        if (Test-Path $extractPath) {
            Remove-Item $extractPath -Recurse -Force
        }
        Expand-Archive -Path $BackupPath -DestinationPath $extractPath -Force
        $BackupPath = $extractPath
        Write-Host "Archive extracted to: $extractPath" -ForegroundColor Green
    }
    
    # Restore code files
    $codeBackupPath = Join-Path $BackupPath "code"
    if (Test-Path $codeBackupPath) {
        Write-Host "Restoring code files..." -ForegroundColor Cyan
        & robocopy $codeBackupPath $RestorePath /E /R:3 /W:1 /MT:8 /NFL /NDL /NP
        if ($LASTEXITCODE -le 7) {
            Write-Host "Code files restored successfully" -ForegroundColor Green
        } else {
            Write-Host "Warning: Some code files may not have been restored properly" -ForegroundColor Yellow
        }
    }
    
    # Restore database
    $dbBackupPath = Join-Path $BackupPath "database\management.db"
    if (Test-Path $dbBackupPath) {
        Write-Host "Restoring database..." -ForegroundColor Cyan
        Copy-Item $dbBackupPath (Join-Path $RestorePath "management.db") -Force
        Write-Host "Database restored successfully" -ForegroundColor Green
    } else {
        Write-Host "Warning: Database backup not found" -ForegroundColor Yellow
    }
    
    # Restore configuration files
    $configBackupPath = Join-Path $BackupPath "config"
    if (Test-Path $configBackupPath) {
        Write-Host "Restoring configuration files..." -ForegroundColor Cyan
        $configFiles = Get-ChildItem $configBackupPath
        foreach ($file in $configFiles) {
            Copy-Item $file.FullName (Join-Path $RestorePath $file.Name) -Force
        }
        Write-Host "Configuration files restored successfully" -ForegroundColor Green
    }
    
    Write-Host "`n=== Restore Completed ===" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Create virtual environment: python -m venv venv_new" -ForegroundColor White
    Write-Host "2. Activate virtual environment: venv_new\Scripts\activate" -ForegroundColor White
    Write-Host "3. Install dependencies: pip install -r requirements.txt" -ForegroundColor White
    Write-Host "4. Initialize database: python init_db.py" -ForegroundColor White
    Write-Host "5. Start application: python run.py" -ForegroundColor White
    
} catch {
    Write-Host "Error during restore: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}