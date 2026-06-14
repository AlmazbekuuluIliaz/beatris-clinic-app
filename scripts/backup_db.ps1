param(
    [string]$OutputDirectory = "backups"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$BackupDirectory = Join-Path $ProjectRoot $OutputDirectory
New-Item -ItemType Directory -Force -Path $BackupDirectory | Out-Null

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$FileName = "beatris_$Timestamp.sql"
$BackupPath = Join-Path $BackupDirectory $FileName
$ContainerPath = "/tmp/$FileName"

Write-Host "Creating MySQL backup..."

try {
    & docker compose exec -T db sh -c "mysqldump --single-transaction --quick --routines --triggers --events -uroot -p\"`$MYSQL_ROOT_PASSWORD\" \"`$MYSQL_DATABASE\" > '$ContainerPath'"
    if ($LASTEXITCODE -ne 0) {
        throw "mysqldump failed with exit code $LASTEXITCODE."
    }

    & docker compose cp "db:$ContainerPath" $BackupPath
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the backup from the database container."
    }
}
finally {
    & docker compose exec -T db rm -f $ContainerPath 2>$null
}

$Backup = Get-Item -LiteralPath $BackupPath
Write-Host "Backup created: $($Backup.FullName)"
Write-Host "Size: $([math]::Round($Backup.Length / 1MB, 2)) MB"
