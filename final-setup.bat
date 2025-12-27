@echo off
echo ========================================
echo   Final Setup - LMS Application
echo ========================================
echo.

cd /d C:\laragon\www\lms

echo [1/3] Generating application key...
C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe artisan key:generate --force

echo.
echo [2/3] Clearing caches...
C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe artisan config:clear
C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe artisan cache:clear
C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe artisan route:clear

echo.
echo [3/3] Creating storage link...
C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64\php.exe artisan storage:link

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo.
echo 1. Open Laragon and click "Start All"
echo 2. Open HeidiSQL (Database button in Laragon)
echo 3. Create database: lms_database
echo 4. Run: php artisan migrate
echo 5. Access: http://lms.test
echo.
pause
