import streamlit as st
import asyncio
import io
import os
import tempfile
import ctranslate2
import transformers
# MoviePy 2.x+ uses simplified imports
from moviepy import VideoFileClip 
from streamlit_mic_recorder import mic_recorder
from faster_whisper import WhisperModel
import edge_tts

# --- CONFIGURATION ---
st.set_page_config(page_title="Indic Universal Translator", layout="wide")

# --- 1. MULTILINGUAL DICTIONARY (12+ Languages) ---
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

# --- 2. MODEL LOADING & CONVERSION ---
NLLB_SOURCE = "facebook/nllb-200-distilled-600M"
NLLB_CT2_DIR = "nllb-200-ct2-int8"

@st.cache_resource
def load_engines():
    # STT: Faster-Whisper
    stt = WhisperModel("tiny", device="cpu", compute_type="int8")
    
    # MT: NLLB (Auto-convert if needed)
    if not os.path.exists(NLLB_CT2_DIR):
        with st.spinner("Optimizing Models for Indian Languages..."):
            converter = ctranslate2.converters.TransformersConverter(NLLB_SOURCE)
            converter.convert(NLLB_CT2_DIR, quantization="int8")
            
    translator = ctranslate2.Translator(NLLB_CT2_DIR, device="cpu")
    tokenizer = transformers.AutoTokenizer.from_pretrained(NLLB_SOURCE)
    
    return stt, translator, tokenizer

stt_model, translator, tokenizer = load_engines()

# --- 3. HELPER FUNCTIONS ---
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
    
    # 1. STT
    with st.spinner(f"Transcribing {src_display}..."):
        segments, _ = stt_model.transcribe(io.BytesIO(audio_bytes))
        text = " ".join([s.text for s in segments])
        if not text.strip():
            st.warning("No speech detected. Please try again.")
            return
        st.info(f"**Original ({src_display}):** {text}")

    # 2. Translation
    with st.spinner(f"Translating to {tgt_display}..."):
        tokenizer.src_lang = src_code
        source = tokenizer.convert_ids_to_tokens(tokenizer.encode(text))
        results = translator.translate_batch([source], target_prefix=[[tgt_code]])
        target = results[0].hypotheses[0]
        if tgt_code in target: target.remove(tgt_code)
        translated_text = tokenizer.decode(tokenizer.convert_tokens_to_ids(target))
        st.success(f"**{tgt_display}:** {translated_text}")

    # 3. TTS
    with st.spinner("Generating Audio..."):
        try:
            out_audio = asyncio.run(generate_speech(translated_text, tts_voice))
            st.audio(out_audio, format="audio/mp3")
        except Exception as e:
            st.error(f"TTS Error: {e}")

# --- 4. UI LAYOUT ---
st.title("🌐 Indic Universal Translator (Voice & Video)")
tab1, tab2 = st.tabs(["🎙️ Live Voice", "🎥 Upload Video"])

with tab1:
    c1, c2 = st.columns(2)
    with c1: s1 = st.selectbox("I am speaking:", list(INDIC_LANGS.keys()), key="s1")
    with c2: t1 = st.selectbox("Translate to:", list(INDIC_LANGS.keys()), index=1, key="t1")
    
    rec = mic_recorder(start_prompt="⏺️ Record", stop_prompt="⏹️ Stop & Translate", key='rec')
    if rec:
        process_audio_bytes(rec['bytes'], s1, t1)

with tab2:
    c3, c4 = st.columns(2)
    with c3: s2 = st.selectbox("Video Language:", list(INDIC_LANGS.keys()), key="s2")
    with c4: t2 = st.selectbox("Translate to:", list(INDIC_LANGS.keys()), index=1, key="t2")
    
    vid_file = st.file_uploader("Upload Video File", type=["mp4", "mov", "avi"])
    
    if vid_file:
        st.video(vid_file)
        if st.button("🚀 Extract & Translate"):
            # Create a temporary file to store the uploaded video
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
                tmp_vid.write(vid_file.read())
                tmp_vid_path = tmp_vid.name
            
            audio_path = tmp_vid_path.replace(".mp4", ".wav")
            
            try:
                with st.spinner("Extracting audio from video..."):
                    # MoviePy v2.2.1 syntax
                    with VideoFileClip(tmp_vid_path) as video:
                        if video.audio is None:
                            st.error("This video has no audio track.")
                        else:
                            video.audio.write_audiofile(audio_path, logger=None)
                            
                            with open(audio_path, "rb") as f:
                                vid_audio_bytes = f.read()
                            
                            process_audio_bytes(vid_audio_bytes, s2, t2)
            except Exception as e:
                st.error(f"Video Processing Error: {e}")
            finally:
                # Cleanup temporary files
                if os.path.exists(tmp_vid_path): os.remove(tmp_vid_path)
                if os.path.exists(audio_path): os.remove(audio_path)