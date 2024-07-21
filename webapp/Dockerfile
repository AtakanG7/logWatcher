# Use the official Apache image from the Docker Hub
FROM httpd:latest

# Copy your custom Apache configuration file to the container
COPY /webapp/apache.conf /usr/local/apache2/conf/httpd.conf

# Copy your web content to the container
COPY /webapp/index.html /usr/local/apache2/htdocs/

# Expose port 80 to the host
EXPOSE 80

# Start Apache when the container starts
CMD ["httpd-foreground"]

