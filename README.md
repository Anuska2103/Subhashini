# 🌐 Indic Universal Translator

A comprehensive multilingual speech-to-speech translation system designed specifically for Indian languages. This application enables real-time voice translation and video audio translation across 12+ Indian languages using state-of-the-art Speech-to-Text (STT), Machine Translation (MT), and Text-to-Speech (TTS) models.

## 🎯 Project Overview

The Indic Universal Translator is a Streamlit-based web application that seamlessly translates spoken language from one Indian language to another in real-time. It supports both live microphone input and video file processing, making it versatile for various use cases such as:

- **Real-time Communication**: Translate conversations between people speaking different Indian languages
- **Content Localization**: Convert video content audio from one language to another
- **Accessibility**: Help bridge language barriers across India's diverse linguistic landscape
- **Educational Tools**: Assist in language learning and cross-cultural communication

### Key Features

✨ **12+ Indian Languages Support**: English, Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Punjabi, Urdu, Assamese, and Sanskrit

🎙️ **Live Voice Translation**: Record audio directly from your microphone and get instant translations

🎥 **Video Audio Translation**: Upload video files and extract audio for translation

🚀 **Optimized Performance**: Uses quantized models for fast inference on CPU

🎯 **High-Quality Output**: Neural TTS voices for natural-sounding speech synthesis

## 🤖 Models Used

### 1. Speech-to-Text (STT)
- **Model**: [Faster-Whisper](https://github.com/guillaumekln/faster-whisper)
- **Base Model**: OpenAI Whisper (`tiny` variant)
- **Size**: ~75MB
- **Quantization**: INT8
- **Device**: CPU-optimized
- **Description**: A highly efficient reimplementation of Whisper using CTranslate2, providing faster transcription with lower memory footprint. The tiny model is specifically chosen for real-time performance while maintaining good accuracy for Indian language accents.

### 2. Machine Translation (MT)
- **Model**: [NLLB-200 (No Language Left Behind)](https://huggingface.co/facebook/nllb-200-distilled-600M)
- **Variant**: `facebook/nllb-200-distilled-600M`
- **Size**: ~600M parameters (distilled version)
- **Quantization**: INT8 (auto-converted using CTranslate2)
- **Supported Languages**: 200+ languages including all major Indian languages
- **Description**: Meta's state-of-the-art multilingual translation model that supports low-resource languages. The distilled version provides a good balance between quality and speed. The model is automatically converted to CTranslate2 format with INT8 quantization for faster inference.

### 3. Text-to-Speech (TTS)
- **Service**: [Edge-TTS](https://github.com/rany2/edge-tts)
- **Provider**: Microsoft Azure Neural Voices
- **Quality**: Neural TTS with natural prosody
- **Voices**: Language-specific neural voices optimized for Indian languages
- **Description**: Leverages Microsoft's high-quality neural TTS voices that are specifically trained for Indian language phonetics and natural speech patterns. Provides realistic and natural-sounding output.

### Supported Language Mappings

| Language   | NLLB Code   | TTS Voice               |
|-----------|-------------|-------------------------|
| English   | eng_Latn    | en-IN-NeerjaNeural     |
| Hindi     | hin_Deva    | hi-IN-SwaraNeural      |
| Bengali   | ben_Beng    | bn-IN-TanishaaNeural   |
| Marathi   | mar_Deva    | mr-IN-AarohiNeural     |
| Tamil     | tam_Taml    | ta-IN-PallaviNeural    |
| Telugu    | tel_Telu    | te-IN-ShrutiNeural     |
| Gujarati  | guj_Gujr    | gu-IN-DhwaniNeural     |
| Kannada   | kan_Knda    | kn-IN-SapnaNeural      |
| Malayalam | mal_Mlym    | ml-IN-SobhanaNeural    |
| Punjabi   | pan_Guru    | pa-IN-OjasNeural       |
| Urdu      | urd_Arab    | ur-PK-UzmaNeural       |
| Assamese  | asm_Beng    | bn-IN-TanishaaNeural   |
| Sanskrit  | san_Deva    | hi-IN-SwaraNeural      |

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **FFmpeg**: Required for audio/video processing
- **Operating System**: Windows, Linux, or macOS
- **RAM**: Minimum 4GB recommended
- **Internet Connection**: Required for initial model downloads and Edge-TTS

## 🚀 Installation

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd stt-tts
```

### Step 2: Install FFmpeg

FFmpeg is required for video processing and audio extraction.

#### Windows
1. Download FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
2. Extract and add to system PATH
3. Verify installation:
   ```bash
   ffmpeg -version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install ffmpeg
```

#### macOS
```bash
brew install ffmpeg
```

### Step 3: Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### Step 4: Activate Virtual Environment

#### Windows
```bash
venv\Scripts\activate
```

#### Linux/macOS
```bash
source venv/bin/activate
```

### Step 5: Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- `streamlit` - Web application framework
- `faster-whisper` - Speech-to-text engine
- `ctranslate2` - Optimized inference for translation models
- `transformers` - Hugging Face transformers library
- `edge-tts` - Text-to-speech synthesis
- `moviepy` - Video processing library
- `streamlit-mic-recorder` - Audio recording component

### Step 6: First-Time Model Setup

On the first run, the application will automatically:
1. Download the Faster-Whisper tiny model (~75MB)
2. Download the NLLB-200 distilled model (~1.2GB)
3. Convert NLLB to CTranslate2 INT8 format (saves to `nllb-200-ct2-int8/`)

**Note**: This process may take 5-10 minutes depending on your internet speed and CPU. The converted models are cached for subsequent runs.

## 🎮 Usage

### Starting the Application

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate your virtual environment (if not already activated)

3. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```

4. The application will open in your default browser at `http://localhost:8501`

### Live Voice Translation

1. Navigate to the **"🎙️ Live Voice"** tab
2. Select your **source language** (the language you're speaking)
3. Select your **target language** (the language you want to translate to)
4. Click the **"⏺️ Record"** button to start recording
5. Speak clearly into your microphone
6. Click **"⏹️ Stop & Translate"** when finished
7. The app will:
   - Transcribe your speech to text
   - Translate it to the target language
   - Generate and play audio in the target language

### Video Audio Translation

1. Navigate to the **"🎥 Upload Video"** tab
2. Select the **video language** (original audio language)
3. Select your **target language** for translation
4. Click **"Browse files"** and upload your video (MP4, MOV, or AVI)
5. Click **"🚀 Extract & Translate"** button
6. The app will:
   - Extract audio from the video
   - Transcribe the audio
   - Translate to target language
   - Generate and play translated audio

## 📁 Project Structure

```
stt-tts/
├── backend/
│   ├── main.py                      # Main Streamlit application
│   ├── requirements.txt             # Python dependencies
│   ├── packages.txt                 # System packages (FFmpeg)
│   ├── nllb-200-ct2-int8/          # Converted NLLB model (auto-generated)
│   │   ├── config.json
│   │   └── shared_vocabulary.json
│   ├── outputs/                     # Temporary audio outputs
│   └── src/
│       ├── audio_captures.py       # Audio recording utilities
│       ├── stt_engine.py           # Speech-to-Text engine wrapper
│       ├── translator.py           # Translation engine wrapper
│       └── tts_engine.py           # Text-to-Speech engine wrapper
└── README.md                        # This file
```

## ⚙️ Configuration

### Model Settings

You can modify model configurations in [main.py](backend/main.py):

```python
# Change Whisper model size (tiny, base, small, medium, large)
stt = WhisperModel("tiny", device="cpu", compute_type="int8")

# Change NLLB model source
NLLB_SOURCE = "facebook/nllb-200-distilled-600M"

# Change quantization level (int8, int16, float16, float32)
converter.convert(NLLB_CT2_DIR, quantization="int8")
```

### Adding More Languages

To add more languages, update the `INDIC_LANGS` dictionary in [main.py](backend/main.py):

```python
INDIC_LANGS = {
    "Language Name": ("nllb_code", "tts-voice-id"),
    # Add more languages here
}
```

Find NLLB language codes [here](https://github.com/facebookresearch/flores/blob/main/flores200/README.md#languages-in-flores-200) and Edge-TTS voices using:

```bash
edge-tts --list-voices
```

## 🔧 Troubleshooting

### Common Issues

**1. FFmpeg Not Found**
```
Error: FFmpeg not found
```
**Solution**: Install FFmpeg and ensure it's added to system PATH.

**2. Model Download Fails**
```
Error: Failed to download model
```
**Solution**: Check your internet connection and Hugging Face availability. You may need to set up Hugging Face authentication for some models.

**3. Memory Issues**
```
Error: Out of memory
```
**Solution**: Try using smaller Whisper model variants or increase system RAM.

**4. Microphone Not Working**
```
Error: Cannot access microphone
```
**Solution**: Grant browser microphone permissions and check system audio settings.

**5. TTS Connection Error**
```
Error: edge-tts connection failed
```
**Solution**: Check internet connection. Edge-TTS requires active internet for synthesis.

### Performance Optimization

- **For faster STT**: Use `tiny` model (current default)
- **For better accuracy**: Use `base` or `small` Whisper models
- **For GPU acceleration**: Change `device="cpu"` to `device="cuda"` (requires CUDA setup)
- **For lower memory usage**: Ensure INT8 quantization is enabled

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for:
- Additional language support
- Performance improvements
- Bug fixes
- Documentation enhancements
- New features

## 📝 License

This project is open-source and available under the MIT License.

## 🙏 Acknowledgments

- [Meta AI - NLLB-200](https://github.com/facebookresearch/fairseq/tree/nllb) for the multilingual translation model
- [OpenAI - Whisper](https://github.com/openai/whisper) for the speech recognition model
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) for optimized Whisper implementation
- [Microsoft Azure](https://azure.microsoft.com/en-us/services/cognitive-services/text-to-speech/) for high-quality neural TTS voices
- [Streamlit](https://streamlit.io/) for the web application framework

## 📧 Contact

For questions, suggestions, or support, please open an issue on the repository.

---

**Made with ❤️ for bridging linguistic barriers across India**
