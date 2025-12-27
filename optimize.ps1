# Rocket LMS Performance Optimization Script
# Run this in the lms directory

Write-Host "=== Rocket LMS Performance Optimizer ===" -ForegroundColor Cyan
Write-Host ""

# Step 1: Clear all caches first
Write-Host "[1/6] Clearing old caches..." -ForegroundColor Yellow
php artisan cache:clear 2>$null
php artisan config:clear 2>$null
php artisan view:clear 2>$null
Remove-Item "bootstrap\cache\*.php" -Force -ErrorAction SilentlyContinue
Write-Host "  Done!" -ForegroundColor Green

# Step 2: Optimize config
Write-Host "[2/6] Caching configuration..." -ForegroundColor Yellow
php artisan config:cache
Write-Host "  Done!" -ForegroundColor Green

# Step 3: Cache views
Write-Host "[3/6] Caching Blade views..." -ForegroundColor Yellow
php artisan view:cache
Write-Host "  Done!" -ForegroundColor Green

# Step 4: Optimize autoloader
Write-Host "[4/6] Optimizing Composer autoloader..." -ForegroundColor Yellow
composer dump-autoload --optimize --no-dev 2>$null
if ($LASTEXITCODE -ne 0) {
    composer dump-autoload --optimize 2>$null
}
Write-Host "  Done!" -ForegroundColor Green

# Step 5: Update .env for production
Write-Host "[5/6] Setting production environment..." -ForegroundColor Yellow
$envFile = Get-Content ".env" -Raw
$envFile = $envFile -replace 'APP_DEBUG=true', 'APP_DEBUG=false'
$envFile = $envFile -replace 'APP_ENV=local', 'APP_ENV=production'
$envFile | Set-Content ".env" -NoNewline
Write-Host "  Done!" -ForegroundColor Green

# Step 6: Laravel optimize
Write-Host "[6/6] Running Laravel optimize..." -ForegroundColor Yellow
php artisan optimize 2>$null
Write-Host "  Done!" -ForegroundColor Green

Write-Host ""
Write-Host "=== Optimization Complete! ===" -ForegroundColor Green
Write-Host ""
Write-Host "Performance improvements applied:" -ForegroundColor White
Write-Host "  - Config cached (faster config loading)" -ForegroundColor Gray
Write-Host "  - Views cached (faster Blade compilation)" -ForegroundColor Gray
Write-Host "  - Autoloader optimized (faster class loading)" -ForegroundColor Gray
Write-Host "  - Debug mode disabled (less overhead)" -ForegroundColor Gray
Write-Host ""
Write-Host "NOTE: Route caching is NOT possible with Closure-based routes." -ForegroundColor Yellow
Write-Host ""
Write-Host "Restart Apache/Nginx for changes to take effect!" -ForegroundColor Cyan
