from vocal_isolation1 import isolate_vocals
from speech_to_text1 import extract_text
from language_detect1 import detect_language, SUPPORTED_LANGUAGES

import os
import gc
from datetime import datetime

# Optional: Reduce TensorFlow logging noise
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def normalize_path(path: str) -> str:
    path = path.strip().strip('"').strip("'")
    if path.startswith('\\\\wsl.localhost\\'):
        path = path.replace('\\\\wsl.localhost\\Ubuntu-22.04\\', '/')
        path = path.replace('\\', '/')
    return path

def main():
    """
    Main function to orchestrate the multi-language audio transcription process.
    """
    print("🎵 Multi-Language Audio Transcription Tool")
    print("=" * 50)
    print("🎵 Enter the path to your audio file (MP3/WAV):")
    audio_path = input("→ ").strip()
    audio_path = normalize_path(audio_path)

    if not os.path.isfile(audio_path):
        print(f"❌ File not found at: {audio_path}")
        return

    try:
        print("🎤 Isolating vocals...")
        vocal_path = isolate_vocals(audio_path)
    except Exception as e:
        print(f"❌ Failed to isolate vocals: {e}")
        return

    try:
        print("\n🌐 Detecting language...")
        detected_language = detect_language(vocal_path)
        language_name = SUPPORTED_LANGUAGES.get(detected_language, 'English')
        print(f"✅ Language detected: {language_name} ({detected_language})")
    except Exception as e:
        print(f"❌ Language detection failed: {e}")
        print("Defaulting to English...")
        detected_language = 'en'
        language_name = 'English'

    try:
        print(f"\n🗣️ Extracting lyrics (speech-to-text) in {language_name}...")
        raw_transcription = extract_text(vocal_path, language_code=detected_language).strip()
        
        if not raw_transcription:
            print("❌ No lyrics were transcribed.")
            print("\n💡 Troubleshooting tips:")
            print("  • Try a song with clearer vocals")
            print("  • Ensure the audio has actual singing/lyrics (not instrumental)")
            print("  • Check if the song has very quiet or heavily processed vocals")
            print("  • Some songs may have vocals that are too mixed with instruments")
            print("  • Try adjusting the audio volume or quality")
            return
        
        print(f"\n📝 Transcription Results ({language_name}):")
        print("=" * 60)
        print(raw_transcription)
        print("=" * 60)
        print(f"\n✅ Transcription completed successfully!")
        print(f"📊 Language: {language_name}")
        print(f"📏 Length: {len(raw_transcription)} characters")
        print(f"📄 Word count: {len(raw_transcription.split())}")
        
        # Optional: Save to file
        save_option = input("\n💾 Save transcription to file? (y/n): ").strip().lower()
        if save_option == 'y':
            base_name = os.path.splitext(os.path.basename(audio_path))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{base_name}_transcription_{detected_language}_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Audio File: {audio_path}\n")
                f.write(f"Language: {language_name} ({detected_language})\n")
                f.write(f"Transcription Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 50 + "\n\n")
                f.write(raw_transcription)
                
            print(f"✅ Transcription saved to: {output_file}")
            
    except Exception as e:
        print(f"❌ Speech-to-text failed: {e}")
        return

    finally:
        # Cleanup
        gc.collect()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    main()