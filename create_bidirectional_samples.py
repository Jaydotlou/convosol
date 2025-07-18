#!/usr/bin/env python3
"""
Create Bidirectional Conversation Samples
Generates realistic back-and-forth conversations between multiple speakers
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

def create_bidirectional_audio(scenario_name, speakers_scripts, output_filename):
    """Create bidirectional conversation audio using OpenAI TTS with different voices"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Different voices for different speakers
    voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    try:
        print(f"Creating bidirectional conversation: {scenario_name}")
        
        # Create temp directory
        os.makedirs("temp_audio", exist_ok=True)
        
        # Generate audio for each speaker
        audio_files = []
        
        for i, (speaker, script) in enumerate(speakers_scripts):
            voice = voices[i % len(voices)]
            print(f"  - Creating audio for {speaker} (voice: {voice})")
            
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=script,
                speed=1.0
            )
            
            temp_path = f"temp_audio/{speaker.lower().replace(' ', '_')}.mp3"
            response.stream_to_file(temp_path)
            audio_files.append(temp_path)
            
            # Small delay to avoid rate limiting
            time.sleep(0.5)
        
        # For now, save the first speaker's audio as the main file
        # In a full implementation, you'd merge the audio files with proper timing
        os.makedirs("sample_audio", exist_ok=True)
        output_path = f"sample_audio/{output_filename}"
        
        # Copy the first file as the main output (simplified)
        import shutil
        shutil.copy(audio_files[0], output_path)
        
        # Clean up temp files
        for file in audio_files:
            os.remove(file)
        os.rmdir("temp_audio")
        
        print(f"    Audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"    Error creating audio: {str(e)}")
        return None

def main():
    """Create bidirectional conversation samples"""
    
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_api_key_here":
        print("Please set your OpenAI API key in .env file first")
        return
    
    print("Creating Bidirectional Conversation Samples")
    print("=" * 50)
    
    # More realistic bidirectional scenarios
    scenarios = [
        {
            "name": "Safety Meeting Discussion",
            "filename": "safety_meeting_discussion.mp3",
            "speakers_scripts": [
                ("Safety Manager", "Good morning everyone. Let's start with our weekly safety review. John, can you update us on the PPE compliance status?"),
                ("John", "Thanks Sarah. I'm pleased to report that PPE compliance is at 95% this week. However, we had two incidents in the welding department where safety glasses weren't worn properly."),
                ("Safety Manager", "That's concerning. Mary, as the welding supervisor, what's your assessment of the situation?"),
                ("Mary", "I've noticed that some of our newer employees are still adjusting to the safety protocols. I think we need additional training sessions, especially for the lockout tagout procedures."),
                ("Safety Manager", "Agreed. Let's schedule mandatory refresher training for all welding department staff. We cannot compromise on safety standards.")
            ]
        },
        {
            "name": "Quality Control Investigation",
            "filename": "quality_control_investigation.mp3", 
            "speakers_scripts": [
                ("QC Manager", "We need to discuss the quality issues found in yesterday's production batch. Mike, what did your inspection reveal?"),
                ("Mike", "We found defects in 15% of the units from batch 237. The main issue is with the tolerance levels on the mounting brackets. They're consistently 0.2mm outside specifications."),
                ("QC Manager", "That's unacceptable. Lisa, from the engineering perspective, what could be causing this deviation?"),
                ("Lisa", "I suspect it's a calibration issue with machine number 3. The tool wear indicators show it's due for maintenance. We should halt production on that machine immediately."),
                ("QC Manager", "Agreed. Mike, please coordinate with maintenance to get machine 3 recalibrated. We need to quarantine all parts from the affected batches until we can verify quality.")
            ]
        },
        {
            "name": "Production Planning Crisis",
            "filename": "production_planning_crisis.mp3",
            "speakers_scripts": [
                ("Production Manager", "We have a critical situation. Our main customer just moved up their delivery deadline by two weeks. Tom, what's our current capacity?"),
                ("Tom", "We're already running at 85% capacity. To meet the new deadline, we'd need to increase to 110% capacity, which means overtime and possibly weekend shifts."),
                ("Production Manager", "Jennifer, what's the impact on our other orders if we prioritize this customer?"),
                ("Jennifer", "We'd have to delay three smaller orders by at least a week. The revenue impact would be significant, but this customer represents 40% of our annual business."),
                ("Production Manager", "We need to make this work. Tom, authorize overtime for the next two weeks. Jennifer, contact the affected customers immediately to negotiate new delivery dates.")
            ]
        }
    ]
    
    created_files = []
    
    for scenario in scenarios:
        print(f"\nProcessing: {scenario['name']}")
        
        # Create a combined script for the conversation
        combined_script = ""
        for speaker, script in scenario['speakers_scripts']:
            combined_script += f"{speaker}: {script} "
        
        # For simplicity, create audio with the combined script using one voice
        # In a full implementation, you'd alternate voices and add proper timing
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=combined_script
            )
            
            os.makedirs("sample_audio", exist_ok=True)
            output_path = f"sample_audio/{scenario['filename']}"
            response.stream_to_file(output_path)
            
            created_files.append(output_path)
            print(f"  Audio saved: {output_path}")
            
        except Exception as e:
            print(f"  Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("Bidirectional Conversation Samples Complete!")
    print(f"Created {len(created_files)} files:")
    
    for file_path in created_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024
            print(f"   • {file_path} ({file_size:.1f} KB)")
    
    print("\nThese samples demonstrate:")
    print("• Multi-speaker conversations")
    print("• Realistic back-and-forth dialogue")
    print("• Manufacturing-specific scenarios")
    print("• Different speaker roles and responsibilities")
    
    # Cost estimate
    total_chars = sum(len(" ".join([script for _, script in scenario['speakers_scripts']])) for scenario in scenarios)
    estimated_cost = (total_chars / 1000) * 0.015
    print(f"\nEstimated cost: ${estimated_cost:.3f}")

if __name__ == "__main__":
    main() 