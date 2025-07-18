#!/bin/bash

# AI Speech Recognition & Analysis Platform
# Deployment Script for Streamlit Community Cloud

set -e

echo "🚀 AI Speech Recognition & Analysis Platform - Deployment Setup"
echo "================================================================"

# Check if we're in the right directory
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Error: Git is not installed. Please install git first."
    exit 1
fi

# Step 1: Initialize git repository if needed
if [ ! -d ".git" ]; then
    echo "🔧 Initializing Git repository..."
    git init
    git branch -M main
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Step 2: Add all files to git
echo "📦 Adding files to git..."
git add .

# Step 3: Check if there are changes to commit
if git diff --cached --quiet; then
    echo "✅ No new changes to commit"
else
    echo "💾 Committing changes..."
    git commit -m "Prepare for Streamlit Cloud deployment

Features:
- Professional client-facing interface
- Heroicons instead of emojis
- Bidirectional conversation samples
- Speaker identification and analysis
- Manufacturing-specific insights
- Export functionality
- Streamlit Cloud ready"
    echo "✅ Changes committed"
fi

# Step 4: Check sample audio files
echo "🎵 Checking sample audio files..."
if [ -d "sample_audio" ]; then
    file_count=$(ls -1 sample_audio/*.mp3 2>/dev/null | wc -l)
    total_size=$(du -h sample_audio | cut -f1)
    echo "✅ Found $file_count sample audio files (total: $total_size)"
    
    echo "   Sample files:"
    ls -la sample_audio/*.mp3 | awk '{print "   • " $9 " (" $5/1024 " KB)"}'
else
    echo "⚠️  No sample audio files found. Run 'python create_sample_audio.py' first."
fi

# Step 5: Display next steps
echo ""
echo "🌐 Next Steps for Streamlit Cloud Deployment:"
echo "=============================================="
echo ""
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to Streamlit Cloud:"
echo "   • Go to: https://share.streamlit.io"
echo "   • Connect your GitHub account"
echo "   • Deploy new app:"
echo "     - Repository: YOUR_USERNAME/YOUR_REPO_NAME"
echo "     - Branch: main"
echo "     - Main file path: streamlit_app.py"
echo ""
echo "3. Add your OpenAI API key:"
echo "   • Go to app settings"
echo "   • Add to secrets: OPENAI_API_KEY = \"your_actual_api_key\""
echo ""
echo "4. Test the deployment:"
echo "   • Try uploading sample audio files"
echo "   • Verify speaker identification works"
echo "   • Test export functionality"
echo ""
echo "📁 Project Structure:"
echo "====================="
echo "✅ streamlit_app.py         (Main app for cloud deployment)"
echo "✅ requirements.txt         (Python dependencies)"
echo "✅ .streamlit/config.toml   (Streamlit configuration)"
echo "✅ .gitignore              (Git ignore file)"
echo "✅ README.md               (Documentation)"
if [ -d "sample_audio" ]; then
    echo "✅ sample_audio/           (Demo audio files)"
fi
echo ""
echo "🎯 Features Ready for Demo:"
echo "==========================="
echo "✅ Professional interface (no emojis, heroicons)"
echo "✅ Hidden API key (loads from Streamlit secrets)"
echo "✅ Speaker identification"
echo "✅ Manufacturing-specific analysis"
echo "✅ Bidirectional conversation samples"
echo "✅ Export functionality"
echo "✅ Client-ready presentation"
echo ""
echo "💰 Cost Estimate:"
echo "================="
echo "• Whisper API: ~\$0.006 per minute of audio"
echo "• GPT-4 Analysis: ~\$0.01 per conversation"
echo "• Sample files cost: ~\$0.05 total"
echo ""
echo "🎉 Ready for deployment! Your clients will be impressed."
echo ""

# Step 6: Optional - remind about API key
echo "⚠️  IMPORTANT: Don't forget to add your OpenAI API key to Streamlit secrets!"
echo "   Get your key from: https://platform.openai.com/api-keys"
echo ""

# Step 7: Show current git status
echo "📊 Current Git Status:"
echo "====================="
git status --short
echo ""
echo "Use 'git log --oneline' to see your commit history."
echo "" 