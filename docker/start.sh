#!/bin/bash
set -e

echo "🚀 Starting Laravel application..."

# Ensure storage directories exist and have correct permissions
echo "📁 Setting up storage directories..."
mkdir -p /var/www/storage/framework/cache/data
mkdir -p /var/www/storage/framework/sessions
mkdir -p /var/www/storage/framework/views
mkdir -p /var/www/storage/logs
mkdir -p /var/www/bootstrap/cache

# Create cache-bootstrap.php if it doesn't exist (required by public/index.php)
if [ ! -f /var/www/storage/framework/cache/cache-bootstrap.php ]; then
    echo "<?php // Laravel Cache Bootstrap" > /var/www/storage/framework/cache/cache-bootstrap.php
fi

# Set permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache
chmod -R 775 /var/www/storage /var/www/bootstrap/cache

# Clear all Laravel caches (important for existing installations)
echo "🧹 Clearing Laravel caches..."
php artisan config:clear 2>/dev/null || true
php artisan cache:clear 2>/dev/null || true
php artisan view:clear 2>/dev/null || true
php artisan route:clear 2>/dev/null || true

# Only optimize if not in debug mode
if [ "$APP_DEBUG" != "true" ]; then
    echo "⚡ Optimizing application..."
    php artisan config:cache 2>/dev/null || true
    php artisan route:cache 2>/dev/null || true
    php artisan view:cache 2>/dev/null || true
fi

echo "✅ Laravel ready!"


# Start supervisor to run nginx and php-fpm
echo "🚀 Starting web services..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

