#!/bin/bash

# Create the main project directory structure
mkdir -p app/nxtep
mkdir -p app/core
mkdir -p app/clients
mkdir -p app/monitoring
mkdir -p app/billing
mkdir -p app/content_manager
mkdir -p app/static/css
mkdir -p app/static/js
mkdir -p app/static/img
mkdir -p app/templates/core
mkdir -p app/templates/clients
mkdir -p app/templates/monitoring
mkdir -p app/templates/billing
mkdir -p app/templates/content_manager

# Create __init__.py files
touch app/nxtep/__init__.py
touch app/core/__init__.py
touch app/clients/__init__.py
touch app/monitoring/__init__.py
touch app/billing/__init__.py
touch app/content_manager/__init__.py

# Copy all the Python files we've created
echo "Copying project files..."

# Print completion message
echo "Setup complete! Your NXTep project structure is ready."
echo "Run 'docker-compose up -d' to start the development environment."
