FROM nginx:alpine

# Copy the custom nginx configuration
COPY docker/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf

# Copy the public directory for static files
COPY public /var/www/public

# Set working directory
WORKDIR /var/www
