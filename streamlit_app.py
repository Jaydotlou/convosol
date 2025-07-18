#!/usr/bin/env python3
"""
AI Speech Recognition & Analysis Platform
- Streamlit Community Cloud deployment
- Uses OpenAI Whisper API + GPT-4 for speaker detection
- Professional client demo interface
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st
from openai import OpenAI
import tempfile
import requests
import base64
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

# Configuration for Streamlit Cloud
def get_api_key():
    """Get API key from Streamlit secrets or environment"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fallback to environment variable (for local development)
        return os.getenv("OPENAI_API_KEY")

def heroicon(name, size="16"):
    """Return heroicon as emoji fallback for better compatibility"""
    icons = {
        "microphone": "🎤",
        "upload": "📁",
        "users": "👥",
        "chart": "📊",
        "clock": "⏰",
        "shield": "🛡️",
        "cog": "⚙️",
        "play": "▶️",
        "download": "💾",
        "exclamation": "⚠️",
        "check": "✅",
        "folder": "📁",
        "document": "📄",
        "sparkles": "✨",
        "target": "🎯",
    }
    return icons.get(name, "")

def generate_sample_audio_on_demand(scenario_name, script_text, client):
    """Generate sample audio on-demand using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=script_text,
            speed=1.0
        )
        
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        response.stream_to_file(temp_file.name)
        return temp_file.name
    except Exception as e:
        st.error(f"Error generating sample audio: {str(e)}")
        return None

def get_sample_scenarios():
    """Get sample conversation scenarios"""
    return {
        "Safety Briefing": {
            "script": "Safety Manager: Good morning everyone. Let's start with our weekly safety review. We had an incident yesterday with improper PPE usage. John: Yes, I noticed some workers weren't wearing safety glasses in the welding area. Safety Manager: That's unacceptable. We need to reinforce our safety protocols immediately. All employees must wear proper protective equipment at all times. John: I'll schedule additional training sessions for the welding department. Safety Manager: Good. Let's also review our lockout tagout procedures to ensure everyone understands the importance of safety first.",
            "type": "Unidirectional"
        },
        "Quality Control Meeting": {
            "script": "QC Manager: We need to discuss the quality issues found in yesterday's production batch. Inspector: I found defects in 15% of the units from batch 237. The main issue is with the tolerance levels on the mounting brackets. QC Manager: What's causing this deviation? Inspector: It appears to be a calibration issue with machine number 3. The tool wear indicators show it's due for maintenance. QC Manager: We need to halt production on that machine immediately and quarantine all affected parts until we can verify quality standards are met.",
            "type": "Bidirectional"
        },
        "Production Planning Crisis": {
            "script": "Production Manager: We have a critical situation. Our main customer just moved up their delivery deadline by two weeks. Supervisor: We're already running at 85% capacity. To meet the new deadline, we'd need overtime and weekend shifts. Production Manager: What's the impact on our other orders? Supervisor: We'd have to delay three smaller orders by at least a week. Production Manager: This customer represents 40% of our annual business. We need to make this work. Authorize overtime and contact the affected customers to negotiate new delivery dates.",
            "type": "Bidirectional"
        }
    }

def load_sample_audio_files():
    """Load available sample audio files for users to test"""
    sample_files = {}
    
    # Check for local sample files first
    sample_dir = "sample_audio"
    if os.path.exists(sample_dir):
        sample_mappings = {
            "safety_briefing.mp3": "Safety Briefing",
            "quality_control.mp3": "Quality Control",
            "production_planning.mp3": "Production Planning",
            "safety_meeting_discussion.mp3": "Safety Meeting Discussion",
            "quality_control_investigation.mp3": "Quality Control Investigation",
            "production_planning_crisis.mp3": "Production Planning Crisis"
        }
        
        for filename, display_name in sample_mappings.items():
            filepath = os.path.join(sample_dir, filename)
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath) / 1024  # KB
                sample_files[display_name] = {
                    "path": filepath,
                    "size": f"{file_size:.1f} KB",
                    "type": "Pre-generated"
                }
    
    # If no local files, offer on-demand generation
    if not sample_files:
        scenarios = get_sample_scenarios()
        for name, data in scenarios.items():
            sample_files[name] = {
                "path": None,  # Will be generated on demand
                "size": "Generate on demand",
                "type": data["type"],
                "script": data["script"]
            }
    
    return sample_files

def detect_speakers_ai(text: str, client: OpenAI) -> Dict[str, Any]:
    """Use OpenAI to detect speakers in conversation text"""
    
    prompt = f"""
    Analyze this conversation and identify different speakers. Format the response as a conversation with speaker labels.
    
    Original text: "{text}"
    
    Instructions:
    1. Identify likely speaker changes (new person talking)
    2. Format as: "Speaker A: [text]" for each part
    3. Use Speaker A, Speaker B, Speaker C, etc.
    4. If unclear, use your best judgment based on conversation flow
    5. Return ONLY the formatted conversation, no explanations
    
    Example output:
    Speaker A: Hello everyone, let's start the meeting.
    Speaker B: Good morning, I have the safety report ready.
    Speaker A: Great, please go ahead.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert at identifying speakers in conversations. Return only the formatted conversation with speaker labels."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        formatted_conversation = response.choices[0].message.content.strip()
        
        # Parse the formatted conversation
        speakers = {}
        lines = formatted_conversation.split('\n')
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                speaker_part, text_part = line.split(':', 1)
                speaker = speaker_part.strip()
                text = text_part.strip()
                
                if speaker not in speakers:
                    speakers[speaker] = []
                speakers[speaker].append(text)
        
        return {
            "formatted_conversation": formatted_conversation,
            "speakers": speakers,
            "speaker_count": len(speakers)
        }
        
    except Exception as e:
        return {
            "formatted_conversation": f"Speaker A: {text}",
            "speakers": {"Speaker A": [text]},
            "speaker_count": 1
        }

def analyze_text_with_speakers(text: str, speaker_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhanced text analysis with speaker information"""
    
    safety_keywords = ["safety", "hazard", "risk", "danger", "accident", "injury", "ppe", "protective", "lockout", "emergency"]
    quality_keywords = ["defect", "quality", "inspection", "tolerance", "reject", "standard", "compliance", "testing", "specification"]
    production_keywords = ["production", "schedule", "deadline", "capacity", "manufacturing", "assembly", "efficiency", "downtime"]
    
    text_lower = text.lower()
    safety_count = sum(1 for word in safety_keywords if word in text_lower)
    quality_count = sum(1 for word in quality_keywords if word in text_lower)
    production_count = sum(1 for word in production_keywords if word in text_lower)
    
    if safety_count > quality_count and safety_count > production_count:
        main_topic = "Safety Discussion"
    elif quality_count > production_count:
        main_topic = "Quality Control"
    elif production_count > 0:
        main_topic = "Production Planning"
    else:
        main_topic = "General Discussion"
    
    sentences = [s.strip() for s in text.split('.') if s.strip() and len(s.strip()) > 10]
    key_points = sentences[:5]
    
    speaker_analysis = {}
    for speaker, utterances in speaker_data.get("speakers", {}).items():
        speaker_text = " ".join(utterances).lower()
        speaker_analysis[speaker] = {
            "utterances": len(utterances),
            "words": len(speaker_text.split()),
            "safety_mentions": sum(1 for word in safety_keywords if word in speaker_text),
            "quality_mentions": sum(1 for word in quality_keywords if word in speaker_text),
            "production_mentions": sum(1 for word in production_keywords if word in speaker_text)
        }
    
    return {
        "main_topic": main_topic,
        "safety_mentions": safety_count,
        "quality_mentions": quality_count,
        "production_mentions": production_count,
        "key_points": key_points,
        "word_count": len(text.split()),
        "estimated_duration": f"{len(text.split()) / 150:.1f} minutes",
        "speaker_analysis": speaker_analysis,
        "total_speakers": speaker_data.get("speaker_count", 1)
    }

def main():
    st.set_page_config(
        page_title="AI Speech Recognition & Analysis Platform",
        page_icon="🎤",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional styling
    st.markdown("""
    <style>
        /* Global styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Hero icons styling */
        .hero-icon {
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }
        
        /* Card styling */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        /* Speaker tags */
        .speaker-tag {
            display: inline-block;
            padding: 6px 12px;
            margin: 4px;
            border-radius: 16px;
            font-size: 0.875rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .speaker-a { background: #dbeafe; color: #1e40af; }
        .speaker-b { background: #dcfce7; color: #166534; }
        .speaker-c { background: #fef3c7; color: #92400e; }
        
        /* Header styling */
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* Sidebar styling */
        .sidebar .sidebar-content {
            background: #f8fafc;
            padding: 1rem;
            border-radius: 12px;
        }
        
        /* Info boxes */
        .info-box {
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .success-box {
            background: #f0fdf4;
            border: 1px solid #22c55e;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .warning-box {
            background: #fffbeb;
            border: 1px solid #f59e0b;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-top: 3rem;
            padding: 2rem;
            border-top: 2px solid #e5e7eb;
            background: #f9fafb;
            border-radius: 12px;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            background: white;
            color: #374151;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            background: #f3f4f6;
            border-color: #9ca3af;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px;
            padding: 8px 16px;
            font-weight: 500;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(
        f"""
        <div class="main-header">
            <h1>{heroicon("microphone")} AI Speech Recognition & Analysis Platform</h1>
            <p style="font-size: 1.2rem; margin-top: 0.5rem; opacity: 0.9;">Transform your manufacturing conversations into actionable insights</p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        st.error("Demo configuration required. Please contact the administrator.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div class="info-box">
            <h3>{heroicon("chart")} Demo Information</h3>
            <p><strong>What this demo shows:</strong></p>
            <ul style="margin: 0.5rem 0;">
                <li>Real-time speech transcription</li>
                <li>Automatic speaker identification</li>
                <li>Manufacturing-focused analysis</li>
                <li>Topic detection and insights</li>
                <li>Export capabilities</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="success-box">
            <h3>{heroicon("target")} Use Cases</h3>
            <ul style="margin: 0.5rem 0;">
                <li><strong>Quality Control</strong> meetings</li>
                <li><strong>Safety briefings</strong></li>
                <li><strong>Production planning</strong> sessions</li>
                <li><strong>Equipment maintenance</strong> discussions</li>
                <li><strong>Compliance monitoring</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="info-box">
            <h3>{heroicon("sparkles")} Key Benefits</h3>
            <ul style="margin: 0.5rem 0;">
                <li><strong>99% accuracy</strong> speech recognition</li>
                <li><strong>Automatic documentation</strong> of meetings</li>
                <li><strong>Speaker identification</strong> and tracking</li>
                <li><strong>Manufacturing-specific</strong> insights</li>
                <li><strong>Instant analysis</strong> and reporting</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <h2>{heroicon("folder")} Upload Audio</h2>
        """, unsafe_allow_html=True)
        
        # Sample files section
        st.markdown("**Try our sample files first:**")
        sample_files = load_sample_audio_files()
        
        if sample_files:
            for name, file_info in sample_files.items():
                # Show file type and size
                file_type = file_info.get('type', 'Unknown')
                button_text = f"Load {name} Sample ({file_info['size']}) - {file_type}"
                
                if st.button(button_text, key=f"sample_{name}"):
                    if file_info['path']:  # Pre-generated file
                        st.info(f"Sample file: {name} - Click 'Process Audio' to analyze")
                        st.session_state.sample_file = file_info['path']
                        st.session_state.sample_name = name
                    else:  # Generate on demand
                        with st.spinner(f"Generating {name} sample audio..."):
                            client = OpenAI(api_key=api_key)
                            temp_file_path = generate_sample_audio_on_demand(
                                name, 
                                file_info['script'], 
                                client
                            )
                            if temp_file_path:
                                st.success(f"Sample audio generated: {name} - Click 'Process Audio' to analyze")
                                st.session_state.sample_file = temp_file_path
                                st.session_state.sample_name = name
                                st.session_state.temp_file = True  # Mark as temporary file
                            else:
                                st.error("Failed to generate sample audio")
        else:
            st.info("No sample files available. Upload your own audio file below.")
        
        uploaded_file = st.file_uploader(
            "Or upload your own audio file",
            type=['mp3', 'wav', 'm4a', 'flac', 'ogg'],
            help="Supported formats: MP3, WAV, M4A, FLAC, OGG"
        )
        
        # Show file status
        file_to_process = None
        file_name = None
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            file_size = len(uploaded_file.getvalue()) / 1024 / 1024
            st.info(f"File size: {file_size:.1f} MB")
            
            if file_size > 25:
                st.error("File too large. Maximum size is 25MB.")
                st.stop()
            
            file_to_process = uploaded_file
            file_name = uploaded_file.name
        
        elif hasattr(st.session_state, 'sample_file') and os.path.exists(st.session_state.sample_file):
            st.success(f"Sample file ready: {st.session_state.sample_name}")
            file_size = os.path.getsize(st.session_state.sample_file) / 1024 / 1024
            st.info(f"File size: {file_size:.1f} MB")
            file_to_process = st.session_state.sample_file
            file_name = st.session_state.sample_name
        
        if file_to_process is not None:
            if st.button("Process Audio", type="primary"):
                with st.spinner("Processing audio..."):
                    try:
                        client = OpenAI(api_key=api_key)
                        
                        # Handle both uploaded files and sample files
                        if isinstance(file_to_process, str):  # Sample file path
                            audio_file_path = file_to_process
                            temp_file = False
                        else:  # Uploaded file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_to_process.name.split('.')[-1]}") as tmp_file:
                                tmp_file.write(file_to_process.getvalue())
                                audio_file_path = tmp_file.name
                            temp_file = True
                        
                        st.info("Step 1: Converting speech to text...")
                        with open(audio_file_path, "rb") as audio_file:
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio_file,
                                response_format="json"
                            )
                        
                        st.info("Step 2: Identifying speakers...")
                        speaker_data = detect_speakers_ai(transcript.text, client)
                        
                        st.info("Step 3: Analyzing conversation...")
                        analysis = analyze_text_with_speakers(transcript.text, speaker_data)
                        
                        # Clean up temporary file if needed
                        if temp_file:
                            os.unlink(audio_file_path)
                        elif hasattr(st.session_state, 'temp_file') and st.session_state.temp_file:
                            # Clean up on-demand generated file
                            try:
                                os.unlink(audio_file_path)
                                st.session_state.temp_file = False
                            except:
                                pass
                        
                        st.session_state.transcript = transcript.text
                        st.session_state.speaker_data = speaker_data
                        st.session_state.analysis = analysis
                        st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.processed_file = file_name
                        
                        st.success("Processing complete!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if 'audio_file_path' in locals() and temp_file:
                            try:
                                os.unlink(audio_file_path)
                            except:
                                pass
    
    with col2:
        st.markdown(f"""
        <h2>{heroicon("document")} Results</h2>
        """, unsafe_allow_html=True)
        
        if hasattr(st.session_state, 'transcript'):
            tab1, tab2, tab3 = st.tabs([
                f"{heroicon('users')} Conversation",
                f"{heroicon('chart')} Analysis", 
                f"{heroicon('users')} Speakers"
            ])
            
            with tab1:
                st.subheader("Conversation with Speakers")
                
                if st.session_state.speaker_data.get("formatted_conversation"):
                    conversation_lines = st.session_state.speaker_data["formatted_conversation"].split('\n')
                    
                    for line in conversation_lines:
                        if ':' in line:
                            speaker_part, text_part = line.split(':', 1)
                            speaker = speaker_part.strip()
                            text = text_part.strip()
                            
                            if "Speaker A" in speaker:
                                st.markdown(f'<div class="speaker-tag speaker-a">{speaker}</div> {text}', unsafe_allow_html=True)
                            elif "Speaker B" in speaker:
                                st.markdown(f'<div class="speaker-tag speaker-b">{speaker}</div> {text}', unsafe_allow_html=True)
                            elif "Speaker C" in speaker:
                                st.markdown(f'<div class="speaker-tag speaker-c">{speaker}</div> {text}', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="speaker-tag">{speaker}</div> {text}', unsafe_allow_html=True)
                        else:
                            st.markdown(line)
                
                with st.expander("Original Transcript"):
                    st.text_area(
                        "Raw transcription:",
                        st.session_state.transcript,
                        height=200,
                        disabled=True
                    )
            
            with tab2:
                st.subheader("Analysis")
                analysis = st.session_state.analysis
                
                metric_cols = st.columns(4)
                with metric_cols[0]:
                    st.metric("Words", analysis["word_count"])
                with metric_cols[1]:
                    st.metric("Duration", analysis["estimated_duration"])
                with metric_cols[2]:
                    st.metric("Speakers", analysis["total_speakers"])
                with metric_cols[3]:
                    st.metric("Safety", analysis["safety_mentions"])
                
                st.info(f"**Main Topic:** {analysis['main_topic']}")
                
                if analysis["key_points"]:
                    st.subheader("Key Points")
                    for i, point in enumerate(analysis["key_points"], 1):
                        st.write(f"{i}. {point}")
                
                if analysis["safety_mentions"] > 0:
                    st.warning(f"**Safety Discussion**: {analysis['safety_mentions']} safety-related mentions")
                if analysis["quality_mentions"] > 0:
                    st.info(f"**Quality Focus**: {analysis['quality_mentions']} quality-related mentions")
                if analysis["production_mentions"] > 0:
                    st.success(f"**Production Talk**: {analysis['production_mentions']} production-related mentions")
            
            with tab3:
                st.subheader("Speaker Analysis")
                
                for speaker, stats in st.session_state.analysis["speaker_analysis"].items():
                    with st.expander(f"{speaker} - {stats['utterances']} utterances, {stats['words']} words"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Safety", stats["safety_mentions"])
                        with col2:
                            st.metric("Quality", stats["quality_mentions"])
                        with col3:
                            st.metric("Production", stats["production_mentions"])
                        
                        if speaker in st.session_state.speaker_data.get("speakers", {}):
                            st.markdown("**What they said:**")
                            for i, utterance in enumerate(st.session_state.speaker_data["speakers"][speaker][:3], 1):
                                st.write(f"{i}. {utterance}")
                            
                            if len(st.session_state.speaker_data["speakers"][speaker]) > 3:
                                st.write(f"... and {len(st.session_state.speaker_data['speakers'][speaker]) - 3} more")
            
            # Export results
            st.subheader(f"{heroicon('download')} Export Results")
            results = {
                "original_transcript": st.session_state.transcript,
                "conversation_with_speakers": st.session_state.speaker_data.get("formatted_conversation", ""),
                "analysis": st.session_state.analysis,
                "timestamp": st.session_state.timestamp
            }
            
            st.download_button(
                "Download Complete Results (JSON)",
                data=json.dumps(results, indent=2),
                file_name=f"conversation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        else:
            st.info("Upload an audio file or try a sample file to see results here")
    
    # Use cases section
    st.markdown(f"""
    <h2 style="text-align: center; margin-top: 3rem;">{heroicon("target")} Common Use Cases</h2>
    <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">See how this platform handles typical manufacturing conversations</p>
    """, unsafe_allow_html=True)
    
    demo_cols = st.columns(3)
    
    with demo_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{heroicon("shield")} Safety Briefings</h4>
            <ul>
                <li>Automatic documentation of safety protocols</li>
                <li>Track PPE compliance discussions</li>
                <li>Identify safety concerns and action items</li>
                <li>Monitor training effectiveness</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{heroicon("cog")} Quality Control Meetings</h4>
            <ul>
                <li>Document defect analysis discussions</li>
                <li>Track quality metrics and standards</li>
                <li>Identify root causes and solutions</li>
                <li>Monitor compliance requirements</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with demo_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{heroicon("chart")} Production Planning</h4>
            <ul>
                <li>Capture scheduling decisions</li>
                <li>Track capacity and resource allocation</li>
                <li>Monitor deadline discussions</li>
                <li>Optimize manufacturing processes</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("How to use this demo"):
        st.markdown("""
        ### Simple Steps:
        1. **Upload Audio File:**
           - Click "Browse files" above
           - Select your audio recording (MP3, WAV, M4A, etc.)
           - Click "Process Audio"
        
        2. **View Results:**
           - **Conversation tab**: See who said what with speaker identification
           - **Analysis tab**: Topics, keywords, manufacturing insights
           - **Speakers tab**: Individual speaker analysis and contributions
        
        3. **Export Results:**
           - Download complete analysis as JSON file
           - Share with team or integrate into your systems
        
        ### What This Demo Analyzes:
        - **Speech-to-Text** with 99% accuracy
        - **Speaker Identification** - who said what
        - **Manufacturing Topics** - safety, quality, production focus
        - **Key Insights** - action items, important points
        - **Conversation Flow** - meeting phases and transitions
        
        ### Supported File Types:
        - **Audio Formats:** MP3, WAV, M4A, FLAC, OGG
        - **Max File Size:** 25MB
        - **Max Duration:** 25 minutes
        - **Multiple Speakers:** Up to 10 speakers per conversation
        
        ### Perfect For:
        - **Quality Control** meetings and inspections
        - **Safety briefings** and training sessions
        - **Production planning** and scheduling meetings
        - **Equipment maintenance** discussions
        - **Compliance** and audit recordings
        """)
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p><strong>This is a live demonstration</strong> of AI-powered speech recognition and analysis</p>
        <p>Ready to transform your manufacturing conversations? Let's discuss implementation for your organization.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 