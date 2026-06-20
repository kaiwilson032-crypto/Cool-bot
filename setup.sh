#!/bin/bash
# Quick setup script for All In One Setup bot

echo "🤖 All In One Setup Bot - Quick Start"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env from example
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your DISCORD_TOKEN"
fi

echo ""
echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "   1. Edit .env and add your Discord bot token"
echo "   2. Run: python bot.py"
echo ""
