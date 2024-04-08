# Use official MySQL 8.0 image as base image
FROM mysql:8.0

# Set environment variables for MySQL
ENV MYSQL_ROOT_PASSWORD=password

# Copy SQL script to Docker container
COPY init.sql /docker-entrypoint-initdb.d/

# Expose port 3306 to the outside world
EXPOSE 3306