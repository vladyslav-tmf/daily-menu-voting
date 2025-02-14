#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Print waiting message and connection details
echo "Waiting for postgres..."
echo "Host: $POSTGRES_HOST"
echo "Port: $POSTGRES_PORT"

# Wait for PostgreSQL to be ready
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done

echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Execute the main command passed to the container
exec "$@"
