#!/usr/bin/env python3
"""
Sample Audio Generator for Demo
Creates realistic manufacturing conversation audio files for demonstration purposes.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

def create_sample_audio(scenario_name, script_text, output_filename):
    """Create sample audio using OpenAI TTS"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        print(f"🎤 Creating audio for: {scenario_name}")
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Professional, neutral voice
            input=script_text
        )
        
        # Create samples directory if it doesn't exist
        os.makedirs("sample_audio", exist_ok=True)
        
        # Save audio file
        output_path = f"sample_audio/{output_filename}"
        response.stream_to_file(output_path)
        
        print(f"✅ Audio saved: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error creating audio: {str(e)}")
        return None

def main():
    """Create sample audio files for demo"""
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_api_key_here":
        print("❌ Please set your OpenAI API key in .env file first")
        return
    
    print("🎯 Creating Sample Audio Files for Demo")
    print("=" * 50)
    
    # Sample scenarios
    scenarios = [
        {
            "name": "Safety Briefing",
            "filename": "safety_briefing.mp3",
            "script": """
            Good morning everyone. Before we start today's shift, let's review the safety procedures. 
            John, please ensure all team members are wearing their PPE correctly. 
            Mary, what's the status on the lockout tagout training? 
            We need to make sure everyone understands the emergency evacuation procedures. 
            Remember, safety is our top priority. Any questions about the hazard assessment?
            """
        },
        {
            "name": "Quality Control Meeting",
            "filename": "quality_control.mp3",
            "script": """
            Let's discuss the quality issues from yesterday's production run. 
            Sarah, we found defects in batch 42. Can you inspect the tolerance levels? 
            The specifications weren't met on several components. 
            Mike, what's your analysis of the root cause? 
            We need to address these quality problems immediately to meet our standards. 
            The inspection results show we need better calibration of our testing equipment.
            """
        },
        {
            "name": "Production Planning",
            "filename": "production_planning.mp3",
            "script": """
            Good morning team. Let's discuss next week's production schedule. 
            Tom, what's our current manufacturing capacity? 
            We have a major deadline approaching and need to optimize our processes. 
            Lisa, can you review the resource allocation for the assembly line? 
            There's a bottleneck in the packaging department we need to address. 
            We need to increase efficiency and reduce downtime to meet our targets.
            """
        }
    ]
    
    # Create audio files
    created_files = []
    for scenario in scenarios:
        print(f"\n📝 Processing: {scenario['name']}")
        
        file_path = create_sample_audio(
            scenario["name"],
            scenario["script"],
            scenario["filename"]
        )
        
        if file_path:
            created_files.append(file_path)
    
    # Summary
    print("\n" + "=" * 50)
    print("🎉 Sample Audio Creation Complete!")
    print(f"📁 Created {len(created_files)} sample files:")
    
    for file_path in created_files:
        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"   • {file_path} ({file_size:.1f} KB)")
    
    print("\n🚀 Ready for Demo!")
    print("   1. Run: ./run.sh")
    print("   2. Upload these sample files to show clients")
    print("   3. Demonstrate the analysis capabilities")
    
    # Cost estimate
    total_chars = sum(len(s["script"]) for s in scenarios)
    estimated_cost = (total_chars / 1000) * 0.015  # $0.015 per 1K characters
    print(f"\n💰 Estimated cost: ${estimated_cost:.3f}")

if __name__ == "__main__":
    main() 