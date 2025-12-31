#!/bin/bash
set -e

echo "🚀 Starting Laravel application initialization..."

# Wait for database to be ready (if using external DB)
if [ -n "$DB_HOST" ]; then
    echo "⏳ Waiting for database connection..."
    max_tries=30
    count=0
    until php artisan db:show > /dev/null 2>&1 || [ $count -eq $max_tries ]; do
        count=$((count+1))
        echo "Database not ready yet... attempt $count/$max_tries"
        sleep 2
    done
    
    if [ $count -eq $max_tries ]; then
        echo "⚠️  Warning: Could not connect to database, continuing anyway..."
    else
        echo "✅ Database connection established"
    fi
fi

# Ensure storage directories exist and have correct permissions
echo "📁 Setting up storage directories..."
mkdir -p /var/www/storage/framework/cache/data
mkdir -p /var/www/storage/framework/sessions
mkdir -p /var/www/storage/framework/views
mkdir -p /var/www/storage/logs
mkdir -p /var/www/bootstrap/cache

# Set permissions
chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache
chmod -R 775 /var/www/storage /var/www/bootstrap/cache

# Clear and cache Laravel configuration
echo "🔧 Optimizing Laravel..."
php artisan config:clear || true
php artisan cache:clear || true
php artisan view:clear || true
php artisan route:clear || true

# Only cache if not in debug mode
if [ "$APP_DEBUG" != "true" ]; then
    php artisan config:cache || true
    php artisan route:cache || true
    php artisan view:cache || true
fi

# Run migrations if AUTO_MIGRATE is set
if [ "$AUTO_MIGRATE" = "true" ]; then
    echo "🗄️  Running database migrations..."
    php artisan migrate --force || echo "⚠️  Migration failed, continuing..."
fi

echo "✅ Laravel initialization complete!"

# Start supervisor to run nginx and php-fpm
echo "🚀 Starting services..."
exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
