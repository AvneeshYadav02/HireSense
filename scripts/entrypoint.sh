#!/bin/sh
set -e

# Run database migrations
flask db upgrade

# Start the application
exec python run.py
