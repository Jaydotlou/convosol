# Streamlit Cloud Deployment Guide

## 🚀 Deploy to Streamlit Cloud

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Set the main file path: `streamlit_app.py`
5. Click "Deploy"

### Step 3: Configure API Key (CRITICAL)
1. Go to your app dashboard
2. Click the **⚙️ Settings** button
3. Go to **"Secrets"** tab
4. Add this configuration:
```toml
OPENAI_API_KEY = "your-actual-api-key-here"
```
5. Click "Save"

### Step 4: Get OpenAI API Key
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key (starts with `sk-proj-...`)
4. Add it to Streamlit Cloud secrets

## 🔧 Local Development

### Option 1: Using .env file
Create `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### Option 2: Using Streamlit secrets
Create `.streamlit/secrets.toml`:
```toml
OPENAI_API_KEY = "your-api-key-here"
```

## ⚠️ Important Notes

- **Never commit API keys to git** - they're excluded by `.gitignore`
- **Both methods work locally** - the app checks both `.env` and `secrets.toml`
- **Streamlit Cloud only uses secrets** - `.env` files are not deployed
- **API key is required** - app will show clear error if missing

## 🎯 Test Your Deployment

1. Visit your Streamlit Cloud app URL
2. You should see the full interface (not an error)
3. Try uploading an audio file or using samples
4. Verify the OpenAI API connection works

## 💰 Cost Estimate

- **Whisper API**: $0.006 per minute of audio
- **GPT-4 mini**: ~$0.01 per conversation analysis
- **10 minutes of audio**: ~$0.07 total 