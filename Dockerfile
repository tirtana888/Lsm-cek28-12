FROM php:8.1-fpm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip \
    libzip-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libicu-dev \
    libbz2-dev \
    libgmp-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libsqlite3-dev

# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-configure intl \
    && docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip intl bz2 gmp curl xml

# Install IonCube Loader
RUN curl -o ioncube.tar.gz https://downloads.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz \
    && tar -xvzf ioncube.tar.gz \
    && mv ioncube/ioncube_loader_lin_8.1.so $(php -r "echo ini_get('extension_dir');") \
    && echo "zend_extension=ioncube_loader_lin_8.1.so" > /usr/local/etc/php/conf.d/00-ioncube.ini \
    && rm -rf ioncube.tar.gz ioncube

# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
ENV COMPOSER_MEMORY_LIMIT=-1

# Set working directory
WORKDIR /var/www

# Copy existing application directory contents
COPY . /var/www

# Declare ARGs that Coolify passes
ARG APP_KEY
ARG APP_ENV=production
ARG APP_DEBUG=false
ARG APP_URL=http://localhost

# Map ARGs to ENVs so they are available during build (important for Laravel discovery)
ENV APP_KEY=${APP_KEY}
ENV APP_ENV=${APP_ENV}
ENV APP_DEBUG=${APP_DEBUG}
ENV APP_URL=${APP_URL}

# Self-update composer to be sure
RUN composer self-update

# Install dependencies (Ignore scripts first to ensure vendors are installed)
# We remove --no-scripts later at runtime or in a custom entrypoint if needed,
# but for now, we just want to pass the build phase.
RUN composer install --no-dev --optimize-autoloader --no-scripts --no-interaction --ignore-platform-reqs

# Removed: RUN composer run-script post-autoload-dump
# (This will be handled automatically when the container starts or via an entrypoint)

# Set permissions
RUN chown -R www-data:www-data /var/www/storage /var/www/bootstrap/cache

EXPOSE 9000
CMD ["php-fpm"]
