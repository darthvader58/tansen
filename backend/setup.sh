#!/bin/bash

# Music Transcription API - Setup Script

echo "🎵 Setting up Music Transcription API Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed. Docker is recommended for running Redis."
    echo "   You can install it from: https://docs.docker.com/get-docker/"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration!"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p temp_uploads
mkdir -p processed_files
mkdir -p logs

# Check for Firebase credentials
if [ ! -f firebase-credentials.json ]; then
    echo "⚠️  Firebase credentials not found!"
    echo "   Please download firebase-credentials.json from Firebase Console"
    echo "   and place it in the backend/ directory."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Add firebase-credentials.json to backend/ directory"
echo "   3. Start Redis: docker run -d -p 6379:6379 redis:7-alpine"
echo "   4. Run the API: uvicorn app.main:app --reload"
echo ""
echo "Or use Docker Compose:"
echo "   docker-compose up --build"
echo ""
echo "📚 API Documentation will be available at:"
echo "   http://localhost:8000/docs"
echo ""
