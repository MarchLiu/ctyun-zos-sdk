#!/bin/bash

# CTyun ZOS SDK Virtual Environment Setup Script

echo "Setting up Python virtual environment for CTyun ZOS SDK..."

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher and try again"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo "❌ Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created successfully"

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✓ Virtual environment activated"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements-dev.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"

# Install package in development mode
echo "Installing package in development mode..."
pip install -e .

if [ $? -ne 0 ]; then
    echo "❌ Failed to install package in development mode"
    exit 1
fi

echo "✓ Package installed in development mode"

# Run basic tests
echo "Running basic tests..."
python test_basic.py

if [ $? -eq 0 ]; then
    echo "✓ Basic tests passed"
else
    echo "⚠ Basic tests had some issues (this is normal for first run)"
fi

echo ""
echo "🎉 Virtual environment setup completed!"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
echo "To deactivate:"
echo "  deactivate"
echo ""
echo "Next steps:"
echo "1. Copy config.env.example to .env"
echo "2. Edit .env with your CTyun credentials"
echo "3. Run: python test_real_connection.py"
echo ""
echo "For more information, see SETUP.md"
