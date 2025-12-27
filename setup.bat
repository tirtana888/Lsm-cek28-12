@echo off
echo ========================================
echo   LMS Application - Laragon Setup
echo ========================================
echo.

REM Check if .env exists
echo [1/7] Checking .env file...
if not exist .env (
    echo   Creating .env file...
    (
        echo APP_NAME=LMS_Application
        echo APP_ENV=local
        echo APP_KEY=
        echo APP_DEBUG=true
        echo APP_URL=http://localhost
        echo.
        echo DB_CONNECTION=mysql
        echo DB_HOST=127.0.0.1
        echo DB_PORT=3306
        echo DB_DATABASE=lms_database
        echo DB_USERNAME=root
        echo DB_PASSWORD=
        echo.
        echo BROADCAST_DRIVER=log
        echo CACHE_DRIVER=file
        echo FILESYSTEM_DISK=local
        echo QUEUE_CONNECTION=sync
        echo SESSION_DRIVER=file
        echo SESSION_LIFETIME=120
        echo.
        echo MAIL_MAILER=smtp
        echo MAIL_HOST=mailhog
        echo MAIL_PORT=1025
    ) > .env
    echo   [OK] .env file created!
) else (
    echo   [OK] .env file exists!
)

echo.
echo ========================================
echo   Next Steps - Run These Commands:
echo ========================================
echo.
echo 1. Add PHP to PATH or use full path
echo    Set PATH=C:\laragon\bin\php\php-8.1.10-nts-Win32-vs16-x64;%%PATH%%
echo.
echo 2. Install Composer dependencies:
echo    composer install
echo.
echo 3. Generate application key:
echo    php artisan key:generate
echo.
echo 4. Install Node dependencies:
echo    npm install
echo.
echo 5. Build assets:
echo    npm run dev
echo.
echo 6. Create database 'lms_database' in HeidiSQL
echo.
echo 7. Run migrations:
echo    php artisan migrate
echo.
echo 8. Start Laragon and access:
echo    http://localhost/Source/public
echo.
echo ========================================
echo.
pause
