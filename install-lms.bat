 @echo off
echo ========================================
echo   Installing LMS Dependencies
echo ========================================
echo.

cd /d C:\laragon\www\lms

echo [1/4] Setting up environment...
set PATH=C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64;C:\laragon\bin\composer;%PATH%

echo [2/4] Installing Composer dependencies...
echo This may take 10-20 minutes. Please wait...
composer install --no-dev --ignore-platform-reqs --prefer-dist

echo.
echo [3/4] Generating application key...
php artisan key:generate

echo.
echo [4/4] Clearing caches...
php artisan config:clear
php artisan cache:clear

echo.
echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open Laragon and click "Start All"
echo 2. Create database "lms_database" in HeidiSQL
echo 3. Run: php artisan migrate
echo 4. Access: http://lms.test
echo.
pause
