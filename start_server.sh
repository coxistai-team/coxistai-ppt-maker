#!/bin/bash

# Start the AI Presentation Generator Service
echo "🚀 Starting AI Presentation Generator Service..."

# Set environment variables
export RENDER_DISK_PATH=./persistent_data
export FLASK_APP=ppt_flask.py
export FLASK_ENV=development

# Create persistent data directory if it doesn't exist
mkdir -p ./persistent_data

# Check if Python dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start the Flask server
echo "🌐 Starting server on http://localhost:5002"
echo "📊 Health check: http://localhost:5002/health"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

python test_server.py 