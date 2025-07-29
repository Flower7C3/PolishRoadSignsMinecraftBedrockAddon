#!/bin/bash

# Python Virtual Environment Setup Script
# For macOS development

echo "🖥️ Setting up Python virtual environment..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7+ first."
    exit 1
fi

# Check if venv module is available
if ! python3 -c "import venv" &> /dev/null; then
    echo "❌ Python venv module is not available. Please install Python 3.7+ with venv support."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created successfully!"
else
    echo "✅ Virtual environment already exists."
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📋 Installing requirements..."
    pip install -r requirements.txt
    echo "✅ Requirements installed successfully!"
else
    echo "⚠️ No requirements.txt found. Skipping dependency installation."
fi

echo ""
echo "🎉 Setup complete! Your virtual environment is ready."
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate, run:"
echo "  deactivate"
echo ""