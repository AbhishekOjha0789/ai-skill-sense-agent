import os
import requests
from ..state import AgentState

def audio_crawler(state: AgentState) -> AgentState:
    print("--- AUDIO CRAWLER: Transcribing audio using lightweight SpeechRecognition ---")
    target_url = state.get("url")
    
    transcript = ""
    temp_audio_path = "temp_audio_file.wav"  # Google recognizer prefers WAV format
    
    try:
        # 1. Download the audio file locally from the URL
        response = requests.get(target_url, timeout=30)
        if response.status_code == 200:
            with open(temp_audio_path, "wb") as f:
                f.write(response.content)
                
            # 2. Transcribe using SpeechRecognition (Free Google Web Speech API wrapper)
            import speech_recognition as sr
            
            r = sr.Recognizer()
            
            with sr.AudioFile(temp_audio_path) as source:
                audio_data = r.record(source)
                
            # Uses the free public Google Speech Recognition tier (no API key needed)
            transcript = r.recognize_google(audio_data)
            print("Successfully transcribed audio file.")
            
        else:
            transcript = "Failed to download audio file for transcription."
            
    except sr.UnknownValueError:
        transcript = "Speech Recognition could not understand the audio."
    except sr.RequestError as e:
        transcript = f"Could not request results from Speech Recognition service; {e}"
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