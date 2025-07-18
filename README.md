# AI Speech Recognition & Analysis Platform

A **professional demo** for showcasing AI-powered speech recognition and manufacturing conversation analysis to clients.

## 🌐 Live Demo

**Deployed on Streamlit Community Cloud**: [Your App URL Here]

## 🚀 Quick Start (Local Development)

1. **Setup** (30 seconds):
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Add API Key** (one time only):
   ```bash
   nano .env
   # Replace 'your_api_key_here' with your actual OpenAI API key
   ```

3. **Create Sample Audio** (optional):
   ```bash
   python create_sample_audio.py
   # or for more realistic bidirectional conversations:
   python create_bidirectional_samples.py
   ```

4. **Run** (5 seconds):
   ```bash
   chmod +x run.sh
   ./run.sh
   ```

5. **Demo to Clients** (2 minutes):
   - Browser opens automatically at `http://localhost:8501`
   - Clean, professional interface (no API key visible to clients)
   - Upload client's audio file or use sample scenarios
   - Click "Process Audio" 
   - Show real-time results with speaker identification
   - Export results to share with client

## 📦 What You Need (Demo Administrator)

- **Python 3.7+**
- **OpenAI API key** (get from https://platform.openai.com/api-keys)
- **Client's audio files** or sample recordings for demo

## 👥 What Your Client Sees

- **Clean, professional interface** - no technical details
- **Simple upload and process** - just drag & drop audio
- **Real-time results** - speaker identification and analysis
- **Export functionality** - download results as JSON
- **No setup required** - they just watch the demo

## 🎯 What It Does

- ✅ **Speech-to-Text** (99% accuracy)
- ✅ **Speaker Identification** (who said what)
- ✅ **Manufacturing Analysis** (safety, quality, production topics)
- ✅ **Key Points Extraction**
- ✅ **Simple Interface** (no complex setup)
- ✅ **Export Results** (JSON format)

## 🔧 What I Replaced

| Heavy Dependencies | Lightweight Replacement |
|-------------------|-------------------------|
| `librosa` (200MB) | OpenAI Whisper API |
| `torchaudio` (500MB) | OpenAI Whisper API |
| `speechbrain` (1GB) | OpenAI Whisper API |
| `pyannote-audio` (300MB) | Simple text-based speaker detection |
| **Total: 2GB+** | **Total: 15MB** |

## 🗣️ Speaker ID - How It Works

Since we removed the heavy models, here's how speaker identification works:

**Old way (heavy):**
- Download 300MB+ AI models
- Complex audio processing
- Real speaker diarization

**New way (lightweight):**
- Use OpenAI to analyze conversation patterns
- Detect speaker changes in text
- Simple but effective for demos

## 🌐 Deploy to Streamlit Community Cloud

### Step 1: Prepare Repository

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

2. **Include Sample Audio** (optional):
   ```bash
   # Create sample audio files
   python create_sample_audio.py
   python create_bidirectional_samples.py
   
   # Add to git
   git add sample_audio/
   git commit -m "Add sample audio files"
   git push
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Connect your GitHub account**
3. **Deploy new app**:
   - Repository: `yourusername/your-repo-name`
   - Branch: `main`
   - Main file path: `streamlit_app.py`
4. **Add your API key**:
   - Go to app settings
   - Add to secrets: `OPENAI_API_KEY = "your_actual_api_key"`
5. **Deploy**

### Step 3: Configure App

The app automatically:
- Uses heroicons instead of emojis
- Loads API key from Streamlit secrets
- Provides professional interface for clients
- Includes sample audio files for testing

## 💰 Cost

**OpenAI Whisper API:**
- **$0.006 per minute** of audio
- **10 minutes = $0.06** (6 cents)
- **1 hour = $0.36** (36 cents)

**OpenAI GPT-4 (for analysis):**
- **~$0.01 per conversation** (1 cent)

## 🔧 Troubleshooting

**"externally-managed-environment" error**
- ✅ **Fixed!** Our setup now uses virtual environment
- Just run `./setup.sh` and it handles everything

**"Command not found: streamlit"**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
streamlit run streamlit_app.py
```

**"Invalid API key"**
- Get key from https://platform.openai.com/api-keys
- For local: Edit .env file: `nano .env`
- For cloud: Add to Streamlit secrets
- Make sure you have credits in your account ($5+ recommended)

**"File too large"**
- OpenAI limit: 25MB
- Use shorter audio or compress file

**"Virtual environment not found"**
- Run setup first: `./setup.sh`
- Then run: `./run.sh`

## 🎯 Demo Content Ideas

**Option 1: Generate Sample Audio** (recommended)
```bash
# Create professional sample audio files
python create_sample_audio.py
# or create more realistic bidirectional conversations
python create_bidirectional_samples.py
```

**Option 2: Use Client's Audio**
- Upload client's actual meeting recordings
- Focus on scenarios relevant to client's industry
- Demonstrate safety, quality, and production use cases
- Show both short (2-3 min) and longer (10+ min) examples

## 📂 File Structure After Setup

```
speechsol/
├── streamlit_app.py             # Main Streamlit app (for cloud deployment)
├── demo.py                      # Local demo app
├── create_sample_audio.py       # Sample audio generator
├── create_bidirectional_samples.py # Bidirectional conversation generator
├── requirements.txt             # Python dependencies
├── setup.sh                    # Setup script (creates venv + .env)
├── run.sh                      # Run script (activates venv + runs demo)
├── .env                        # Your API key (created by setup.sh)
├── venv/                       # Virtual environment (created by setup.sh)
├── .streamlit/                 # Streamlit configuration
│   ├── config.toml
│   └── secrets.toml
├── sample_audio/               # Generated sample files
│   ├── safety_briefing.mp3
│   ├── quality_control.mp3
│   ├── production_planning.mp3
│   ├── safety_meeting_discussion.mp3
│   ├── quality_control_investigation.mp3
│   └── production_planning_crisis.mp3
├── .gitignore                  # Git ignore file
└── README.md                   # This file
```

## 🎯 Features

### Professional Interface
- **No emojis** - Uses heroicons instead
- **Clean design** - Professional look for client demos
- **Hidden complexity** - No API keys or technical details visible to clients

### Bidirectional Conversations
- **Multi-speaker audio** - Realistic back-and-forth dialogue
- **Speaker identification** - AI-powered speaker detection
- **Manufacturing scenarios** - Safety, quality, production planning

### Sample Audio Files
- **Built-in samples** - Ready-to-use demo files
- **Download options** - Clients can try sample files
- **Export results** - JSON format for integration

### Deployment Ready
- **Streamlit Cloud compatible** - One-click deployment
- **Environment configuration** - Automatic setup
- **Professional hosting** - Share with clients via URL

---

**Clean, simple, and professional for client demonstrations!** 🎉 