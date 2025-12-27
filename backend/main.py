import streamlit as st
import asyncio
import io
import os
import tempfile
import logging
import warnings

# --- 1. SILENCE WARNINGS ---
# This stops the 'torch_dtype' warning from appearing in your UI/logs
logging.getLogger("transformers").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", category=DeprecationWarning)

from moviepy import VideoFileClip 
from streamlit_mic_recorder import mic_recorder
from faster_whisper import WhisperModel
import edge_tts

# Import your custom class from translator.py
from src.translator import TranslatorEngine

st.set_page_config(page_title="Indic Universal Translator", layout="wide")

# Constants
INDIC_LANGS = {
    "English": ("eng_Latn", "en-IN-NeerjaNeural"),
    "Hindi": ("hin_Deva", "hi-IN-SwaraNeural"),
    "Bengali": ("ben_Beng", "bn-IN-TanishaaNeural"),
    "Marathi": ("mar_Deva", "mr-IN-AarohiNeural"),
    "Tamil": ("ta-IN-PallaviNeural"), # Mapping to available voices
    "Telugu": ("tel_Telu", "te-IN-ShrutiNeural"),
    "Gujarati": ("guj_Gujr", "gu-IN-DhwaniNeural"),
    "Kannada": ("kan_Knda", "kn-IN-SapnaNeural"),
    "Malayalam": ("mal_Mlym", "ml-IN-SobhanaNeural"),
    "Punjabi": ("pan_Guru", "pa-IN-OjasNeural"),
    "Urdu": ("urd_Arab", "ur-PK-UzmaNeural"),
    "Assamese": ("asm_Beng", "bn-IN-TanishaaNeural"),
    "Sanskrit": ("san_Deva", "hi-IN-SwaraNeural"),
}

NLLB_CT2_DIR = "nllb-200-ct2-int8"

# --- 2. ENGINE LOADER ---
@st.cache_resource
def load_all_engines():
    # Load Speech-to-Text
    stt = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    # Load Translation Engine from your translator.py file
    # We assume the model folder is already in the root
    if not os.path.exists(NLLB_CT2_DIR):
        st.error(f"Critical Error: Folder '{NLLB_CT2_DIR}' not found. Please upload it via Git LFS.")
        st.stop()
        
    mt_engine = TranslatorEngine(model_path=NLLB_CT2_DIR)
    
    return stt, mt_engine

stt_model, mt_engine = load_all_engines()

# --- 3. CORE LOGIC ---
async def generate_speech(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def process_audio_bytes(audio_bytes, src_display, tgt_display):
    src_code, _ = INDIC_LANGS[src_display]
    tgt_code, tts_voice = INDIC_LANGS[tgt_display]
    
    # 1. Speech to Text
    with st.spinner(f"Transcribing {src_display}..."):
        segments, _ = stt_model.transcribe(io.BytesIO(audio_bytes))
        text = " ".join([s.text for s in segments])
        if not text.strip():
            st.warning("No speech detected. Please try again.")
            return
        st.info(f"**Original ({src_display}):** {text}")

    # 2. Translation (Using your new TranslatorEngine)
    with st.spinner(f"Translating to {tgt_display}..."):
        try:
            translated_text = mt_engine.translate(text, src_lang=src_code, tgt_lang=tgt_code)
            st.success(f"**{tgt_display}:** {translated_text}")
        except Exception as e:
            st.error(f"Translation Error: {e}")
            return

    # 3. Text to Speech
    with st.spinner("Generating Audio..."):
        try:
            out_audio = asyncio.run(generate_speech(translated_text, tts_voice))
            st.audio(out_audio, format="audio/mp3")
        except Exception as e:
            st.error(f"TTS Error: {e}")

# --- 4. UI LAYOUT ---
st.title("🌐 Indic Universal Translator")
st.markdown("---")

tab1, tab2 = st.tabs(["🎙️ Live Voice", "🎥 Upload Video"])

with tab1:
    c1, c2 = st.columns(2)
    with c1: s1 = st.selectbox("I am speaking:", list(INDIC_LANGS.keys()), key="s1")
    with c2: t1 = st.selectbox("Translate to:", list(INDIC_LANGS.keys()), index=1, key="t1")
    
    rec = mic_recorder(start_prompt="⏺️ Click to Record", stop_prompt="⏹️ Stop & Translate", key='rec')
    if rec:
        process_audio_bytes(rec['bytes'], s1, t1)

with tab2:
    c3, c4 = st.columns(2)
    with c3: s2 = st.selectbox("Video Language:", list(INDIC_LANGS.keys()), key="s2")
    with c4: t2 = st.selectbox("Translate to:", list(INDIC_LANGS.keys()), index=1, key="t2")
    
    vid_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"])
    
    if vid_file:
        st.video(vid_file)
        if st.button("🚀 Process Video"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                tmp_vid.write(vid_file.read())
                tmp_vid_path = tmp_vid.name
            
            audio_path = tmp_vid_path.replace(".mp4", ".wav")
            
            try:
                with st.spinner("Extracting audio..."):
                    with VideoFileClip(tmp_vid_path) as video:
                        if video.audio is None:
                            st.error("No audio found in video.")
                        else:
                            video.audio.write_audiofile(audio_path, logger=None)
                            with open(audio_path, "rb") as f:
                                vid_audio_bytes = f.read()
                            process_audio_bytes(vid_audio_bytes, s2, t2)
            except Exception as e:
                st.error(f"Video Error: {e}")
            finally:
                if os.path.exists(tmp_vid_path): os.remove(tmp_vid_path)
                if os.path.exists(audio_path): os.remove(audio_path)