#!/usr/bin/env python3
"""
AI Speech Recognition & Analysis Platform
- Clean Streamlit components only
- Proper audio preview with base64 encoding
- No CSS overrides
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any
import streamlit as st
try:
    from openai import OpenAI
except ImportError:
    st.error("OpenAI library not installed. Please install with: pip install openai")
    st.stop()
import tempfile
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable proxy settings that might interfere with OpenAI client on Streamlit Cloud
os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)

def get_api_key():
    """Get API key from Streamlit secrets or environment"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except:
        pass
    
    # Try environment variable (for local development)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key
    
    # Try streamlit secrets as dict access
    try:
        return st.secrets.get("OPENAI_API_KEY")
    except:
        pass
    
    # Return None if not found
    return None

def get_audio_base64(file_path):
    """Convert audio file to base64 for preview"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error loading audio: {str(e)}")
        return None

def create_audio_player(file_path, audio_format="mp3"):
    """Create HTML audio player with base64 data"""
    b64_data = get_audio_base64(file_path)
    if b64_data:
        audio_html = f"""
        <audio controls style="width: 100%;">
            <source src="data:audio/{audio_format};base64,{b64_data}" type="audio/{audio_format}">
            Your browser does not support the audio element.
        </audio>
        """
        return audio_html
    return None

def generate_sample_audio_on_demand(scenario_name, script_text, client):
    """Generate sample audio on-demand using OpenAI TTS"""
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=script_text,
            speed=1.0
        )
        
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
            "type": "Bidirectional"
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
    """Load available sample audio files"""
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
                "path": None,
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
        layout="wide"
    )
    
    # Simple header
    st.title("🎤 AI Speech Recognition & Analysis Platform")
    st.markdown("**Transform your manufacturing conversations into actionable insights**")
    
    # Get API key
    api_key = get_api_key()
    
    if not api_key:
        st.error("🔑 **OpenAI API Key Required**")
        st.warning("**For Streamlit Cloud deployment:**")
        st.code("Go to your app settings → Secrets → Add: OPENAI_API_KEY = 'your-api-key-here'")
        st.warning("**For local development:**")
        st.code("Add your API key to .env file: OPENAI_API_KEY=your-api-key-here")
        st.info("Get your API key from: https://platform.openai.com/api-keys")
        st.stop()
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📁 Upload Audio")
        
        # Sample files section
        st.subheader("Try our sample files first:")
        sample_files = load_sample_audio_files()
        
        if sample_files:
            for name, file_info in sample_files.items():
                st.write(f"**🔊 {name}**")
                st.write(f"Type: {file_info.get('type', 'Audio')} | Size: {file_info['size']}")
                
                # Audio preview if file exists
                if file_info['path'] and os.path.exists(file_info['path']):
                    audio_html = create_audio_player(file_info['path'])
                    if audio_html:
                        st.markdown(audio_html, unsafe_allow_html=True)
                    else:
                        st.info("Audio file ready for processing")
                
                # Buttons
                col_load, col_download = st.columns([3, 1])
                
                with col_load:
                    if st.button(f"Load {name} for Analysis", key=f"sample_{name}"):
                        if file_info['path']:  # Pre-generated file
                            st.success(f"Sample file loaded: {name}")
                            st.session_state.sample_file = file_info['path']
                            st.session_state.sample_name = name
                        else:  # Generate on demand
                            with st.spinner(f"Generating {name} sample audio..."):
                                # Initialize OpenAI client for sample generation
                                try:
                                    client = OpenAI(
                                        api_key=api_key,
                                        timeout=30.0,
                                        max_retries=3
                                    )
                                    temp_file_path = generate_sample_audio_on_demand(
                                        name, 
                                        file_info['script'], 
                                        client
                                    )
                                    if temp_file_path:
                                        st.success(f"Sample audio generated: {name}")
                                        st.session_state.sample_file = temp_file_path
                                        st.session_state.sample_name = name
                                        st.session_state.temp_file = True
                                    else:
                                        st.error("Failed to generate sample audio")
                                except Exception as client_error:
                                    st.error(f"Failed to initialize OpenAI client: {str(client_error)}")
                                    st.error("Cannot generate sample audio without valid API key")
                
                with col_download:
                    if file_info['path'] and os.path.exists(file_info['path']):
                        with open(file_info['path'], "rb") as file:
                            st.download_button(
                                label="Download",
                                data=file.read(),
                                file_name=f"{name.lower().replace(' ', '_')}.mp3",
                                mime="audio/mpeg",
                                key=f"download_{name}"
                            )
                
                st.divider()
        
        # File uploader
        st.subheader("Or upload your own audio file:")
        uploaded_file = st.file_uploader(
            "Choose an audio file",
            type=['mp3', 'wav', 'm4a', 'flac', 'ogg'],
            help="Supported formats: MP3, WAV, M4A, FLAC, OGG"
        )
        
        # Handle file processing
        file_to_process = None
        file_name = None
        cached_audio_bytes = None
        
        if uploaded_file is not None:
            st.success(f"File uploaded: {uploaded_file.name}")
            
            # Cache audio bytes
            cached_audio_bytes = uploaded_file.getvalue()
            file_size = len(cached_audio_bytes) / 1024 / 1024
            st.info(f"File size: {file_size:.1f} MB")
            
            if file_size > 25:
                st.error("File too large. Maximum size is 25MB.")
                st.stop()
            
            # Audio preview for uploaded files
            st.audio(cached_audio_bytes, format=f"audio/{uploaded_file.name.split('.')[-1]}")
            
            file_to_process = uploaded_file
            file_name = uploaded_file.name
        
        elif hasattr(st.session_state, 'sample_file') and os.path.exists(st.session_state.sample_file):
            st.success(f"Sample file ready: {st.session_state.sample_name}")
            file_size = os.path.getsize(st.session_state.sample_file) / 1024 / 1024
            st.info(f"File size: {file_size:.1f} MB")
            file_to_process = st.session_state.sample_file
            file_name = st.session_state.sample_name
        
        # Process button
        if file_to_process is not None:
            if st.button("🚀 Process Audio", type="primary"):
                with st.spinner("Processing audio..."):
                    try:
                        # Initialize OpenAI client with proper error handling
                        try:
                            # Initialize with explicit parameters to avoid proxy injection
                            client = OpenAI(
                                api_key=api_key,
                                timeout=30.0,
                                max_retries=3
                            )
                        except Exception as client_error:
                            st.error(f"Failed to initialize OpenAI client: {str(client_error)}")
                            st.error("This may be due to an invalid API key or proxy configuration issue.")
                            return
                        
                        # Handle file paths
                        if isinstance(file_to_process, str):  # Sample file
                            audio_file_path = file_to_process
                            temp_file = False
                        else:  # Uploaded file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_to_process.name.split('.')[-1]}") as tmp_file:
                                if cached_audio_bytes is not None:
                                    tmp_file.write(cached_audio_bytes)
                                else:
                                    tmp_file.write(file_to_process.getvalue())
                                audio_file_path = tmp_file.name
                            temp_file = True
                        
                        # Process audio
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
                        
                        # Clean up temp file
                        if temp_file:
                            os.unlink(audio_file_path)
                        
                        # Store results
                        st.session_state.transcript = transcript.text
                        st.session_state.speaker_data = speaker_data
                        st.session_state.analysis = analysis
                        st.session_state.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.processed_file = file_name
                        
                        st.success("✅ Processing complete!")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        if 'audio_file_path' in locals() and temp_file:
                            try:
                                os.unlink(audio_file_path)
                            except:
                                pass
    
    with col2:
        st.header("📊 Results")
        
        if hasattr(st.session_state, 'transcript'):
            # Create tabs for results
            tab1, tab2, tab3 = st.tabs(["💬 Conversation", "📈 Analysis", "👥 Speakers"])
            
            with tab1:
                st.subheader("Conversation with Speakers")
                
                if st.session_state.speaker_data.get("formatted_conversation"):
                    conversation_lines = st.session_state.speaker_data["formatted_conversation"].split('\n')
                    
                    for line in conversation_lines:
                        if ':' in line:
                            speaker_part, text_part = line.split(':', 1)
                            speaker = speaker_part.strip()
                            text = text_part.strip()
                            
                            # Display with speaker tags
                            if "Speaker A" in speaker:
                                st.markdown(f"**{speaker}:** {text}")
                            elif "Speaker B" in speaker:
                                st.markdown(f"**{speaker}:** {text}")
                            elif "Speaker C" in speaker:
                                st.markdown(f"**{speaker}:** {text}")
                            else:
                                st.markdown(f"**{speaker}:** {text}")
                        else:
                            st.markdown(line)
                
                with st.expander("View Original Transcript"):
                    st.text_area(
                        "Raw transcription:",
                        st.session_state.transcript,
                        height=200,
                        disabled=True
                    )
            
            with tab2:
                st.subheader("Analysis Summary")
                analysis = st.session_state.analysis
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Words", analysis["word_count"])
                with col2:
                    st.metric("Duration", analysis["estimated_duration"])
                with col3:
                    st.metric("Speakers", analysis["total_speakers"])
                with col4:
                    st.metric("Safety Mentions", analysis["safety_mentions"])
                
                st.info(f"**Main Topic:** {analysis['main_topic']}")
                
                # Key points
                if analysis["key_points"]:
                    st.subheader("Key Points")
                    for i, point in enumerate(analysis["key_points"], 1):
                        st.write(f"{i}. {point}")
                
                # Topic analysis
                if analysis["safety_mentions"] > 0:
                    st.warning(f"🛡️ Safety Discussion: {analysis['safety_mentions']} safety-related mentions")
                if analysis["quality_mentions"] > 0:
                    st.info(f"🔍 Quality Focus: {analysis['quality_mentions']} quality-related mentions")
                if analysis["production_mentions"] > 0:
                    st.success(f"🏭 Production Talk: {analysis['production_mentions']} production-related mentions")
            
            with tab3:
                st.subheader("Speaker Breakdown")
                
                for speaker, stats in st.session_state.analysis["speaker_analysis"].items():
                    with st.expander(f"{speaker} - {stats['utterances']} utterances, {stats['words']} words"):
                        
                        # Speaker metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Safety", stats["safety_mentions"])
                        with col2:
                            st.metric("Quality", stats["quality_mentions"])
                        with col3:
                            st.metric("Production", stats["production_mentions"])
                        
                        # Speaker quotes
                        if speaker in st.session_state.speaker_data.get("speakers", {}):
                            st.markdown("**What they said:**")
                            for i, utterance in enumerate(st.session_state.speaker_data["speakers"][speaker][:3], 1):
                                st.write(f"{i}. {utterance}")
                            
                            if len(st.session_state.speaker_data["speakers"][speaker]) > 3:
                                st.write(f"... and {len(st.session_state.speaker_data['speakers'][speaker]) - 3} more")
            
            # Export results
            st.subheader("📥 Export Results")
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
            st.markdown("### Ready for Analysis")
            st.info("Upload an audio file or try a sample file to see results here.")
            
            st.markdown("**Steps:**")
            st.markdown("1. Choose a sample file or upload your own")
            st.markdown("2. Click 'Process Audio' button")
            st.markdown("3. View results in the tabs above")
    
    # Sidebar
    with st.sidebar:
        st.header("Demo Information")
        
        st.markdown("**What this demo shows:**")
        st.markdown("- Real-time speech transcription")
        st.markdown("- Automatic speaker identification")
        st.markdown("- Manufacturing-focused analysis")
        st.markdown("- Topic detection and insights")
        st.markdown("- Export capabilities")
        
        st.header("Use Cases")
        st.markdown("- **Quality Control** meetings")
        st.markdown("- **Safety briefings**")
        st.markdown("- **Production planning** sessions")
        st.markdown("- **Equipment maintenance** discussions")
        st.markdown("- **Compliance monitoring**")
        
        st.header("Key Benefits")
        st.markdown("- **99% accuracy** speech recognition")
        st.markdown("- **Automatic documentation**")
        st.markdown("- **Speaker identification**")
        st.markdown("- **Manufacturing insights**")
        st.markdown("- **Instant analysis**")

if __name__ == "__main__":
    main() 