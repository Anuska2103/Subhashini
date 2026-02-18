# 🌐 Indic Universal Translator

An end-to-end multimodal AI platform designed to break language barriers by providing real-time voice and video translation across **13 major Indian languages**.

---

## 🚀 Features

- **🎙️ Real-time Voice Translation**: Record your voice, transcribe it instantly, translate it, and hear the results in any natural-sounding target indian language voice.
- **🎥 Video Translation**: Upload `.mp4` or `.mov` files to extract audio, translate speech content, and generate a translated voiceover.
- **🇮🇳 13 Supported Languages**: Includes English, Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, and Sanskrit.
- **⚡ Optimized AI Models**: Uses quantized models (INT8) for fast inference on standard CPUs.

---

## 🏗️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, Vite, TailwindCSS | Fast, responsive UI & state management |
| **Backend** | FastAPI, Uvicorn | High-performance asynchronous API |
| **STT** | Faster Whisper (Tiny) | Efficient Speech-to-Text |
| **Translation**| CTranslate2 + NLLB-200 | Optimized Neural Machine Translation |
| **TTS** | Microsoft Edge TTS | Natural-sounding cloud-based speech synthesis |
| **Video** | MoviePy + FFmpeg | Audio extraction and video processing |

---

## 📁 Project Structure

```text
stt-tts/
├── backend/
│   ├── app.py                # FastAPI server entry point
│   ├── requirements.txt      # Python dependencies
│   ├── nllb-200-ct2-int8/    # Optimized translation model files
│   └── src/                  # Core AI engine modules
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main React UI logic
    │   └── main.jsx          # React entry point
    ├── tailwind.config.js    # Styling configuration
    └── vite.config.js        # Build tool configuration
