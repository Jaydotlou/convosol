#!/bin/bash

echo "🎤 Speech Recognition Demo Setup"
echo "================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install it first."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔑 Creating .env file for API key..."
    cat > .env << EOF
# Add your OpenAI API key here
OPENAI_API_KEY=your_api_key_here
EOF
    echo "⚠️  Please edit .env file and add your OpenAI API key"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "🚀 To run the demo:"
echo "   1. First, activate virtual environment:"
echo "      source venv/bin/activate"
echo "   2. Then run:"
echo "      streamlit run demo.py"
echo ""
echo "🔑 Set up your API key ONCE:"
echo "   1. Get key from https://platform.openai.com/api-keys"
echo "   2. Edit .env file: nano .env"
echo "   3. Replace 'your_api_key_here' with your actual key"
echo ""
echo "📁 Supported audio formats: MP3, WAV, M4A, FLAC, OGG"
echo "📊 Max file size: 25MB" 