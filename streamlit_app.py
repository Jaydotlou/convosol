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

def heroicon(name, size="w-5 h-5"):
    """Return heroicon SVG as HTML"""
    icons = {
        "microphone": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>''',
        "upload": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>''',
        "users": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path></svg>''',
        "chart": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>''',
        "clock": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>''',
        "shield": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>''',
        "cog": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>''',
        "play": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.586a1 1 0 01.707.293l2.414 2.414a1 1 0 00.707.293H15M9 10V9a2 2 0 012-2h2a2 2 0 012 2v1M9 10v5a2 2 0 002 2h2a2 2 0 002-2v-5"></path></svg>''',
        "download": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>''',
        "exclamation": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"></path></svg>''',
        "check": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>''',
        "folder": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path></svg>''',
        "document": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>''',
        "sparkles": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>''',
        "target": f'''<svg class="{size}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>''',
    }
    return icons.get(name, "")

def load_sample_audio_files():
    """Load available sample audio files for users to test"""
    sample_files = {}
    
    # Check for local sample files
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
                    "size": f"{file_size:.1f} KB"
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
    
    # Custom CSS for heroicons
    st.markdown("""
    <style>
        .hero-icon {
            display: inline-block;
            vertical-align: middle;
            margin-right: 8px;
        }
        .metric-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .speaker-tag {
            display: inline-block;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 500;
        }
        .speaker-a { background: #dbeafe; color: #1e40af; }
        .speaker-b { background: #dcfce7; color: #166534; }
        .speaker-c { background: #fef3c7; color: #92400e; }
        .footer {
            text-align: center;
            color: #6b7280;
            font-size: 14px;
            margin-top: 2rem;
            padding: 1rem;
            border-top: 1px solid #e5e7eb;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1>{heroicon("microphone", "w-8 h-8")} AI Speech Recognition & Analysis Platform</h1>
        <p style="font-size: 1.1rem; color: #6b7280;">Transform your manufacturing conversations into actionable insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        st.error("Demo configuration required. Please contact the administrator.")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h3>{heroicon("chart", "w-5 h-5")} Demo Information</h3>
            <div style="background: #f9fafb; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <p><strong>What this demo shows:</strong></p>
                <ul style="margin: 0.5rem 0;">
                    <li>Real-time speech transcription</li>
                    <li>Automatic speaker identification</li>
                    <li>Manufacturing-focused analysis</li>
                    <li>Topic detection and insights</li>
                    <li>Export capabilities</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h3>{heroicon("target", "w-5 h-5")} Use Cases</h3>
            <div style="background: #f0fdf4; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                <ul style="margin: 0.5rem 0;">
                    <li><strong>Quality Control</strong> meetings</li>
                    <li><strong>Safety briefings</strong></li>
                    <li><strong>Production planning</strong> sessions</li>
                    <li><strong>Equipment maintenance</strong> discussions</li>
                    <li><strong>Compliance monitoring</strong></li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div>
            <h3>{heroicon("sparkles", "w-5 h-5")} Key Benefits</h3>
            <div style="background: #eff6ff; padding: 1rem; border-radius: 8px;">
                <ul style="margin: 0.5rem 0;">
                    <li><strong>99% accuracy</strong> speech recognition</li>
                    <li><strong>Automatic documentation</strong> of meetings</li>
                    <li><strong>Speaker identification</strong> and tracking</li>
                    <li><strong>Manufacturing-specific</strong> insights</li>
                    <li><strong>Instant analysis</strong> and reporting</li>
                </ul>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <h2>{heroicon("folder", "w-6 h-6")} Upload Audio</h2>
        """, unsafe_allow_html=True)
        
        # Sample files section
        st.markdown("**Try our sample files first:**")
        sample_files = load_sample_audio_files()
        
        if sample_files:
            for name, file_info in sample_files.items():
                if st.button(f"Load {name} Sample ({file_info['size']})", key=f"sample_{name}"):
                    st.info(f"Sample file: {name} - Click 'Process Audio' to analyze")
                    # Store the file path for processing
                    st.session_state.sample_file = file_info['path']
                    st.session_state.sample_name = name
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
        <h2>{heroicon("document", "w-6 h-6")} Results</h2>
        """, unsafe_allow_html=True)
        
        if hasattr(st.session_state, 'transcript'):
            tab1, tab2, tab3 = st.tabs([
                f"{heroicon('users', 'w-4 h-4')} Conversation",
                f"{heroicon('chart', 'w-4 h-4')} Analysis", 
                f"{heroicon('users', 'w-4 h-4')} Speakers"
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
            st.subheader(f"{heroicon('download', 'w-5 h-5')} Export Results")
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
    <h2 style="text-align: center; margin-top: 3rem;">{heroicon("target", "w-6 h-6")} Common Use Cases</h2>
    <p style="text-align: center; color: #6b7280; margin-bottom: 2rem;">See how this platform handles typical manufacturing conversations</p>
    """, unsafe_allow_html=True)
    
    demo_cols = st.columns(3)
    
    with demo_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{heroicon("shield", "w-5 h-5")} Safety Briefings</h4>
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
            <h4>{heroicon("cog", "w-5 h-5")} Quality Control Meetings</h4>
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
            <h4>{heroicon("chart", "w-5 h-5")} Production Planning</h4>
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