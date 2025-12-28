# Sync to Laragon Script
# Syncs all source files to Laragon www folder

param(
    [string]$LaragonPath = "c:\laragon\www\lms"
)

Write-Host "=== Syncing to Laragon ===" -ForegroundColor Cyan
Write-Host "Target: $LaragonPath" -ForegroundColor Gray
Write-Host ""

# Check if target exists
if (-not (Test-Path $LaragonPath)) {
    Write-Host "Creating target directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $LaragonPath -Force | Out-Null
}

# Sync files
Write-Host "[1/3] Copying files..." -ForegroundColor Yellow
$source = (Get-Location).Path
Copy-Item -Path "$source\*" -Destination $LaragonPath -Recurse -Force -Exclude @("node_modules", ".git", "vendor")
Write-Host "  Done!" -ForegroundColor Green

# Clear caches in target
Write-Host "[2/3] Clearing caches in Laragon..." -ForegroundColor Yellow
Remove-Item "$LaragonPath\storage\framework\views\*" -Force -ErrorAction SilentlyContinue
Remove-Item "$LaragonPath\bootstrap\cache\*.php" -Force -ErrorAction SilentlyContinue
Write-Host "  Done!" -ForegroundColor Green

# Run optimize in target
Write-Host "[3/3] Running optimization in Laragon..." -ForegroundColor Yellow
Push-Location $LaragonPath
php artisan config:cache 2>$null
php artisan view:cache 2>$null
Pop-Location
Write-Host "  Done!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Sync Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White  
Write-Host "  1. Restart Apache in Laragon" -ForegroundColor Gray
Write-Host "  2. Open http://lms.test/admin" -ForegroundColor Gray
Write-Host ""
