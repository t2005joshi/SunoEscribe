# detects the language and make sures the speech_to_text is in the same language... speech_to_text uses Nova-3 by deepgram


# detects the language and make sures the speech_to_text is in the same language... speech_to_text uses Nova-3 by deepgram

import os
import subprocess
import soundfile as sf
import requests
from mp3_wav1 import mp3_to_wav

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "")

# Supported languages mapping
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish', 
    'fr': 'French',
    'de': 'German',
    'hi': 'Hindi',
    'ru': 'Russian',
    'pt': 'Portuguese',
    'ja': 'Japanese',
    'it': 'Italian',
    'nl': 'Dutch'
}

def reencode_wav_for_detection(input_path, output_path):
    """
    Re-encode a WAV file to standard PCM 16-bit mono 44.1kHz using ffmpeg for language detection.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-acodec", "pcm_s16le", "-ar", "44100", "-ac", "1", 
        "-t", "30",  # Use first 30 seconds for language detection
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)

def detect_language(vocal_path: str) -> str:
    """
    Detect the language of the isolated vocal audio using Deepgram Nova-3 API.
    
    Parameters:
        vocal_path (str): Path to the isolated vocal WAV file.
        
    Returns:
        str: Detected language code (e.g., 'en', 'es', 'fr', etc.)
    """
    print("🌐 Detecting language...")
    
    # Use the vocal file directly (it's already a WAV file from Spleeter)
    wav_file = vocal_path
    
    # Create a shorter sample for language detection (first 30 seconds)
    detection_file = wav_file.replace(".wav", "_detection.wav")
    
    try:
        reencode_wav_for_detection(wav_file, detection_file)
        
        # Check the detection file
        info = sf.info(detection_file)
        print(f"Detection file info: {info}")
        print(f"Detection file size: {os.path.getsize(detection_file)} bytes")
        
        # Use Deepgram's language detection endpoint
        url = "https://api.deepgram.com/v1/listen?model=nova-3&detect_language=true&punctuate=true&smart_format=true"
        headers = {
            "Authorization": f"Token {DEEPGRAM_API_KEY}",
            "Content-Type": "audio/wav"
        }
        
        with open(detection_file, "rb") as audio:
            print("Uploading audio for language detection...")
            response = requests.post(url, headers=headers, data=audio)
        
        response.raise_for_status()
        result = response.json()
        
        # Extract detected language from the response
        if "results" in result and "channels" in result["results"]:
            channel = result["results"]["channels"][0]
            
            # Check if language was detected in the metadata
            if "detected_language" in channel:
                detected_language = channel["detected_language"].lower()
                print(f"🎯 Language detected from API: {detected_language}")
            elif "alternatives" in channel and channel["alternatives"]:
                # Check if there's language info in alternatives
                alternative = channel["alternatives"][0]
                if "detected_language" in alternative:
                    detected_language = alternative["detected_language"].lower()
                    print(f"🎯 Language detected from alternative: {detected_language}")
                elif "language" in alternative:
                    detected_language = alternative["language"].lower()
                    print(f"🎯 Language detected from alternative language field: {detected_language}")
                else:
                    # Try to get transcript and use fallback logic
                    transcript = alternative.get("transcript", "")
                    if transcript:
                        # Simple heuristic: if transcript exists and looks reasonable, assume primary language
                        detected_language = "en"  # Default fallback
                        print(f"🎯 No explicit language detected, defaulting to English")
                    else:
                        detected_language = "en"
                        print("🎯 No transcript found, defaulting to English")
            else:
                detected_language = "en"
                print("🎯 No alternatives found, defaulting to English")
        else:
            detected_language = "en"
            print("🎯 Invalid response format, defaulting to English")
        
        # Normalize language code
        if detected_language == "zh-cn" or detected_language == "zh-tw":
            detected_language = "zh"
        elif detected_language == "pt-br":
            detected_language = "pt"
        elif detected_language == "es-419":
            detected_language = "es"
        
        # Check if detected language is in our supported list
        if detected_language in SUPPORTED_LANGUAGES:
            print(f"✅ Using language: {SUPPORTED_LANGUAGES[detected_language]} ({detected_language})")
            return detected_language
        else:
            print(f"⚠️ Detected language '{detected_language}' not in supported list. Defaulting to English.")
            return 'en'
            
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg encoding failed: {e}")
        print("Defaulting to English...")
        return 'en'
    except requests.exceptions.RequestException as e:
        print(f"❌ API request failed: {e}")
        print("Defaulting to English...")
        return 'en'
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
        print("Defaulting to English...")
        return 'en'
    
    finally:
        # Clean up detection file
        if os.path.exists(detection_file):
            try:
                os.remove(detection_file)
            except:
                pass