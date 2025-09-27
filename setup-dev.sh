#!/bin/bash

# Eclari Development Setup Script

echo "🚀 Setting up Eclari development environment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Supabase credentials before running the app!"
    echo "   Instructions are in the .env file."
    exit 1
fi

# Check if node_modules exists
if [ ! -d node_modules ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Build JavaScript
echo "🏗️  Building JavaScript bundle..."
npm run build

# Check if virtual environment exists
if [ ! -d venv ]; then
    echo "🐍 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📚 Installing Python dependencies..."
source venv/bin/activate
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "To run the development server:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run Flask: python app.py"
echo ""
echo "For JavaScript development with auto-rebuild:"
echo "1. In another terminal: npm run dev"
echo ""
echo "🌐 The app will be available at http://localhost:5000"