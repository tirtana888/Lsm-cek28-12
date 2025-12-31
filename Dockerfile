FROM php:8.1-fpm

# Install system dependencies including git (required by composer)
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    curl \
    git \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    libfreetype6-dev \
    libjpeg62-turbo-dev \
    libicu-dev \
    libgmp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip intl gmp

# Install ionCube Loader (for glibc/Debian)
RUN curl -o ioncube.tar.gz https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz \
    && tar -xvzf ioncube.tar.gz \
    && cp ioncube/ioncube_loader_lin_8.1.so $(php -r "echo ini_get('extension_dir');")/ \
    && echo "zend_extension=ioncube_loader_lin_8.1.so" > /usr/local/etc/php/conf.d/00-ioncube.ini \
    && rm -rf ioncube.tar.gz ioncube

# Install Composer
COPY --from=composer:2.7 /usr/bin/composer /usr/bin/composer

# Set working directory
WORKDIR /var/www

# Copy application code
COPY . /var/www

# Install PHP dependencies with fallback
# Try normal install first, if it fails, try with --no-scripts
RUN COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_MEMORY_LIMIT=-1 \
    composer install \
    --no-dev \
    --prefer-dist \
    --no-interaction \
    --ignore-platform-reqs \
    --verbose \
    || COMPOSER_ALLOW_SUPERUSER=1 \
    COMPOSER_MEMORY_LIMIT=-1 \
    composer install \
    --no-dev \
    --prefer-dist \
    --no-scripts \
    --no-interaction \
    --ignore-platform-reqs \
    --verbose

# Generate optimized autoloader
RUN COMPOSER_ALLOW_SUPERUSER=1 composer dump-autoload --optimize --no-dev || true

# Create directories
RUN mkdir -p /run/nginx /var/log/nginx

# Copy PHP-FPM config
COPY docker/php/www.conf /usr/local/etc/php-fpm.d/www.conf

# Copy nginx config
COPY docker/nginx/conf.d/default.conf /etc/nginx/sites-available/default

# Create supervisor config
RUN mkdir -p /etc/supervisor/conf.d
RUN echo "[supervisord]\nnodaemon=true\nuser=root\n\n[program:nginx]\ncommand=nginx -g 'daemon off;'\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nstderr_logfile=/dev/stderr\nstderr_logfile_maxbytes=0\n\n[program:php-fpm]\ncommand=php -d variables_order=EGPCS /usr/local/sbin/php-fpm -F\nautostart=true\nautorestart=true\nstdout_logfile=/dev/stdout\nstdout_logfile_maxbytes=0\nstderr_logfile=/dev/stderr\nstderr_logfile_maxbytes=0" > /etc/supervisor/conf.d/app.conf

# Set permissions and create required directories/files
RUN chown -R www-data:www-data /var/www \
    && chmod -R 755 /var/www/storage \
    && chmod -R 755 /var/www/bootstrap/cache \
    && mkdir -p /var/www/storage/framework/cache \
    && mkdir -p /var/www/storage/framework/sessions \
    && mkdir -p /var/www/storage/framework/views \
    && mkdir -p /var/www/storage/logs \
    && touch /var/www/storage/logs/laravel.log \
    && chown -R www-data:www-data /var/www/storage

# Expose port 80
EXPOSE 80

# Start supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]
