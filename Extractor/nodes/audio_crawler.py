# nodes/audio_crawler.py
import os
import requests
from ..state import AgentState

def audio_crawler(state: AgentState) -> AgentState:
    print("--- AUDIO CRAWLER: Transcribing audio using Speech-to-Text (Whisper) ---")
    target_url = state.get("url")
    
    transcript = ""
    temp_audio_path = "temp_audio_file.mp3"
    
    try:
        # 1. Download the audio file locally from the URL
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            with open(temp_audio_path, "wb") as f:
                f.write(response.content)
                
            # 2. Load Whisper model (e.g., 'base' or 'small' model) and transcribe
            import whisper

            model = whisper.load_model("base")
            result = model.transcribe(temp_audio_path)
            transcript = result.get("text", "")
            
            print("Successfully transcribed audio file.")
        else:
            transcript = "Failed to download audio file for transcription."
            
    except Exception as e:
        print(f"Error during audio transcription: {e}")
        transcript = "Error processing audio transcription."
        
    finally:
        # Clean up temporary audio file if it exists
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            
    return {
        "content": transcript.strip()
    }