#!/bin/bash

echo "🚀 Starting Speech Recognition Demo..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env file exists and has API key
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. You'll need to enter your API key manually."
elif grep -q "your_api_key_here" .env; then
    echo "⚠️  Please edit .env file and add your OpenAI API key"
    echo "   Run: nano .env"
    echo "   Replace 'your_api_key_here' with your actual key"
else
    echo "✅ API key found in .env file"
fi

# Run the demo
echo "🎤 Starting demo..."
streamlit run demo.py 