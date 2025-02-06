#!/bin/sh

# Waits to the database to be available
echo "Waiting for database to be available..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is available. Starting the application..."
exec "$@"