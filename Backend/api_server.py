# uvicorn api_server:app --reload --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from vocal_isolation1 import isolate_vocals
from language_detect1 import detect_language
from speech_to_text1 import extract_text
from language_detect1 import SUPPORTED_LANGUAGES

app = FastAPI()

load_dotenv()  # Load .env file

allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add this OPTIONS handler for preflight requests
@app.options("/api/transcribe")
async def transcribe_options():
    return {"message": "OK"}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    logger.info(f"Received transcription request for file: {audio.filename}")
    
    # Check file size (50MB limit)
    if audio.size and audio.size > 50 * 1024 * 1024:
        logger.error(f"File too large: {audio.size} bytes")
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    
    # Check file type
    if not audio.content_type.startswith('audio/'):
        logger.error(f"Invalid file type: {audio.content_type}")
        raise HTTPException(status_code=400, detail="Please upload an audio file")
    
    # Save uploaded file
    file_ext = os.path.splitext(audio.filename)[-1]
    temp_filename = f"{uuid.uuid4().hex}{file_ext}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)
    
    logger.info(f"Saving file to: {temp_path}")
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        logger.info("File saved successfully, starting vocal isolation...")
        
        # 1. Isolate vocals
        vocal_path = isolate_vocals(temp_path)
        if not vocal_path or not os.path.exists(vocal_path):
            logger.error("Failed to isolate vocals")
            return JSONResponse(
                status_code=200,
                content={"transcription": "", "error": "Failed to isolate vocals from the audio file."}
            )
        
        logger.info("Vocals isolated, detecting language...")
        
        # 2. Detect language
        detected_language = detect_language(vocal_path)
        language_name = SUPPORTED_LANGUAGES.get(detected_language, "English")
        
        logger.info(f"Language detected: {language_name} ({detected_language})")
        
        # 3. Transcribe
        logger.info("Starting transcription...")
        transcription = extract_text(vocal_path, language_code=detected_language).strip()
        
        if not transcription:
            logger.warning("No transcription generated")
            return JSONResponse(
                status_code=200,
                content={"transcription": "", "error": "No lyrics were transcribed."}
            )
        
        logger.info(f"Transcription completed successfully: {len(transcription)} characters")
        
        return {
            "transcription": transcription,
            "language": detected_language,
            "language_name": language_name
        }
        
    except Exception as e:
        logger.error(f"Error during transcription: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"transcription": "", "error": f"Transcription failed: {str(e)}"}
        )
    finally:
        # Clean up uploaded and intermediate files
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
                logger.info("Temporary file cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up temp file: {e}")

# Health check with more info
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "message": "SunoEscribe API is running",
        "upload_dir": UPLOAD_DIR,
        "upload_dir_exists": os.path.exists(UPLOAD_DIR)
    }

@app.get("/ping")
async def ping():
    print("Ping hit")
    return {"status": "alive"}