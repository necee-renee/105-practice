#!/bin/bash

# Meeting Invitation Generator Startup Script

echo "Starting Meeting Invitation Generator..."
echo "========================================"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6 or higher to run this application"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Using Python version: $PYTHON_VERSION"

# Create required directories
mkdir -p templates uploads

# Start the server
echo "Starting server on port 8000..."
echo "Open your browser to: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 server.py