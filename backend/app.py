from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
import io
import os
import tempfile
import logging
import warnings
from typing import Optional

# Silence warnings
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=DeprecationWarning)
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import ctranslate2
import transformers
from moviepy import VideoFileClip
from faster_whisper import WhisperModel
import edge_tts

app = FastAPI(title="Indic Universal Translator API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Language configurations
INDIC_LANGS = {
    "English": ("eng_Latn", "en-IN-NeerjaNeural"),
    "Hindi": ("hin_Deva", "hi-IN-SwaraNeural"),
    "Bengali": ("ben_Beng", "bn-IN-TanishaaNeural"),
    "Marathi": ("mar_Deva", "mr-IN-AarohiNeural"),
    "Tamil": ("tam_Taml", "ta-IN-PallaviNeural"),
    "Telugu": ("tel_Telu", "te-IN-ShrutiNeural"),
    "Gujarati": ("guj_Gujr", "gu-IN-DhwaniNeural"),
    "Kannada": ("kan_Knda", "kn-IN-SapnaNeural"),
    "Malayalam": ("mal_Mlym", "ml-IN-SobhanaNeural"),
    "Punjabi": ("pan_Guru", "pa-IN-OjasNeural"),
    "Urdu": ("urd_Arab", "ur-PK-UzmaNeural"),
    "Assamese": ("asm_Beng", "bn-IN-TanishaaNeural"),
    "Sanskrit": ("san_Deva", "hi-IN-SwaraNeural"),
}

NLLB_SOURCE = "facebook/nllb-200-distilled-600M"
NLLB_CT2_DIR = "nllb-200-ct2-int8"

# Global models
stt_model = None
translator = None
tokenizer = None

@app.on_event("startup")
async def load_models():
    """Load models on startup"""
    global stt_model, translator, tokenizer
    
    print("Loading STT model...")
    stt_model = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    print("Loading translation model...")
    if not os.path.exists(NLLB_CT2_DIR):
        print("First run: Downloading & converting NLLB model...")
        converter = ctranslate2.converters.TransformersConverter(
            NLLB_SOURCE,
            load_as_float16=True
        )
        converter.convert(NLLB_CT2_DIR, quantization="int8", force=True)
    
    translator = ctranslate2.Translator(NLLB_CT2_DIR, device="cpu")
    tokenizer = transformers.AutoTokenizer.from_pretrained(NLLB_SOURCE)
    
    print("✅ All models loaded successfully!")

async def generate_speech(text: str, voice: str) -> bytes:
    """Generate speech using Edge TTS"""
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

@app.get("/")
async def root():
    return {"message": "Indic Universal Translator API", "status": "running"}

@app.get("/languages")
async def get_languages():
    """Get list of supported languages"""
    return {"languages": list(INDIC_LANGS.keys())}

@app.post("/translate-audio")
async def translate_audio(
    audio: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    """Translate audio from source to target language"""
    try:
        # Validate languages
        if source_lang not in INDIC_LANGS or target_lang not in INDIC_LANGS:
            raise HTTPException(status_code=400, detail="Invalid language selection")
        
        src_code, _ = INDIC_LANGS[source_lang]
        tgt_code, tts_voice = INDIC_LANGS[target_lang]
        
        # Read audio bytes
        audio_bytes = await audio.read()
        
        # 1. Transcription
        segments, _ = stt_model.transcribe(io.BytesIO(audio_bytes))
        original_text = " ".join([s.text for s in segments]).strip()
        
        if not original_text:
            raise HTTPException(status_code=400, detail="No speech detected")
        
        # 2. Translation
        tokenizer.src_lang = src_code
        source_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(original_text))
        results = translator.translate_batch([source_tokens], target_prefix=[[tgt_code]])
        target_tokens = results[0].hypotheses[0]
        
        if tgt_code in target_tokens:
            target_tokens.remove(tgt_code)
        
        translated_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(target_tokens))
        
        # 3. Generate speech
        audio_output = await generate_speech(translated_text, tts_voice)
        
        return {
            "original_text": original_text,
            "translated_text": translated_text,
            "audio_base64": audio_output.hex()  # Send as hex string
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/translate-video")
async def translate_video(
    video: UploadFile = File(...),
    source_lang: str = Form(...),
    target_lang: str = Form(...)
):
    """Extract audio from video and translate"""
    try:
        # Validate languages
        if source_lang not in INDIC_LANGS or target_lang not in INDIC_LANGS:
            raise HTTPException(status_code=400, detail="Invalid language selection")
        
        src_code, _ = INDIC_LANGS[source_lang]
        tgt_code, tts_voice = INDIC_LANGS[target_lang]
        
        # Save video temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
            tmp_vid.write(await video.read())
            tmp_vid_path = tmp_vid.name
        
        audio_path = tmp_vid_path.replace(".mp4", ".wav")
        
        try:
            # Extract audio
            with VideoFileClip(tmp_vid_path) as video_clip:
                if not video_clip.audio:
                    raise HTTPException(status_code=400, detail="Video has no audio")
                video_clip.audio.write_audiofile(audio_path, logger=None)
            
            # Process audio
            with open(audio_path, "rb") as f:
                audio_bytes = f.read()
            
            # Transcribe
            segments, _ = stt_model.transcribe(io.BytesIO(audio_bytes))
            original_text = " ".join([s.text for s in segments]).strip()
            
            if not original_text:
                raise HTTPException(status_code=400, detail="No speech detected in video")
            
            # Translate
            tokenizer.src_lang = src_code
            source_tokens = tokenizer.convert_ids_to_tokens(tokenizer.encode(original_text))
            results = translator.translate_batch([source_tokens], target_prefix=[[tgt_code]])
            target_tokens = results[0].hypotheses[0]
            
            if tgt_code in target_tokens:
                target_tokens.remove(tgt_code)
            
            translated_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(target_tokens))
            
            # Generate speech
            audio_output = await generate_speech(translated_text, tts_voice)
            
            return {
                "original_text": original_text,
                "translated_text": translated_text,
                "audio_base64": audio_output.hex()
            }
            
        finally:
            # Cleanup
            if os.path.exists(tmp_vid_path):
                os.remove(tmp_vid_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
