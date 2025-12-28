# LMS Application - Laragon Setup Script
# Run this script in PowerShell from the project directory

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LMS Application - Laragon Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if .env exists
Write-Host "[1/7] Checking .env file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Write-Host "  .env file not found. Creating from template..." -ForegroundColor Red
    
    # Create basic .env content
    $envContent = @"
APP_NAME=LMS_Application
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://localhost

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=lms_database
DB_USERNAME=root
DB_PASSWORD=

BROADCAST_DRIVER=log
CACHE_DRIVER=file
FILESYSTEM_DISK=local
QUEUE_CONNECTION=sync
SESSION_DRIVER=file
SESSION_LIFETIME=120

MAIL_MAILER=smtp
MAIL_HOST=mailhog
MAIL_PORT=1025
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_ENCRYPTION=null
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  ✓ .env file created!" -ForegroundColor Green
} else {
    Write-Host "  ✓ .env file exists!" -ForegroundColor Green
}

# Step 2: Check Laragon PHP
Write-Host ""
Write-Host "[2/7] Checking PHP installation..." -ForegroundColor Yellow
$phpPath = "C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe"
if (Test-Path $phpPath) {
    Write-Host "  ✓ PHP 8.1 found!" -ForegroundColor Green
} else {
    Write-Host "  ✗ PHP not found at expected location!" -ForegroundColor Red
    $phpPath = "php"
}

# Step 3: Check Composer
Write-Host ""
Write-Host "[3/7] Checking Composer..." -ForegroundColor Yellow
$composerPath = "C:\laragon\bin\composer\composer.bat"
if (!(Test-Path $composerPath)) {
    $composerPath = "composer"
}
Write-Host "  Using composer at: $composerPath" -ForegroundColor Gray

# Step 4: Check vendor directory
Write-Host ""
Write-Host "[4/7] Checking dependencies..." -ForegroundColor Yellow
if (!(Test-Path "vendor")) {
    Write-Host "  Vendor directory not found. Need to run: composer install" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Vendor directory exists!" -ForegroundColor Green
}

# Step 5: Check node_modules
Write-Host ""
Write-Host "[5/7] Checking Node dependencies..." -ForegroundColor Yellow
if (!(Test-Path "node_modules")) {
    Write-Host "  Node modules not found. Need to run: npm install" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Node modules exist!" -ForegroundColor Green
}

# Step 6: Check database
Write-Host ""
Write-Host "[6/7] Database configuration..." -ForegroundColor Yellow
Write-Host "  Database: lms_database" -ForegroundColor Gray
Write-Host "  Username: root" -ForegroundColor Gray
Write-Host "  Password: (empty)" -ForegroundColor Gray

# Step 7: Summary
Write-Host ""
Write-Host "[7/7] Setup status check complete!" -ForegroundColor Yellow

# Final Instructions
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Manual Setup Steps Required" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Run these commands in order:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Install Composer dependencies:" -ForegroundColor White
Write-Host "   composer install" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Generate application key:" -ForegroundColor White
Write-Host "   php artisan key:generate" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Install Node dependencies:" -ForegroundColor White
Write-Host "   npm install" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Build frontend assets:" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Create database in HeidiSQL/phpMyAdmin:" -ForegroundColor White
Write-Host "   Database name: lms_database" -ForegroundColor Cyan
Write-Host ""
Write-Host "6. Run migrations:" -ForegroundColor White
Write-Host "   php artisan migrate" -ForegroundColor Cyan
Write-Host ""
Write-Host "7. Clear caches:" -ForegroundColor White
Write-Host "   php artisan optimize:clear" -ForegroundColor Cyan
Write-Host ""
Write-Host "8. Start Laragon and access:" -ForegroundColor White
Write-Host "   http://localhost/Source/public" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
