param(
    [Parameter(Mandatory = $true)]
    [string]$BackupFile,

    [switch]$Force
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$BackupPath = (Resolve-Path -LiteralPath $BackupFile).Path
if ([System.IO.Path]::GetExtension($BackupPath) -ne ".sql") {
    throw "Backup file must have the .sql extension."
}

if (-not $Force) {
    Write-Warning "Restoring will replace matching tables and data in the current Beatris database."
    $Confirmation = Read-Host "Type RESTORE to continue"
    if ($Confirmation -cne "RESTORE") {
        Write-Host "Restore cancelled."
        exit 0
    }
}

$ContainerPath = "/tmp/beatris_restore_$([guid]::NewGuid().ToString('N')).sql"

Write-Host "Copying backup to the MySQL container..."

try {
    & docker compose cp $BackupPath "db:$ContainerPath"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not copy the backup to the database container."
    }

    Write-Host "Restoring database..."
    & docker compose exec -T db sh -c "mysql -uroot -p\"`$MYSQL_ROOT_PASSWORD\" \"`$MYSQL_DATABASE\" < '$ContainerPath'"
    if ($LASTEXITCODE -ne 0) {
        throw "Database restore failed with exit code $LASTEXITCODE."
    }
}
finally {
    & docker compose exec -T db rm -f $ContainerPath 2>$null
}

Write-Host "Database restored from: $BackupPath"
