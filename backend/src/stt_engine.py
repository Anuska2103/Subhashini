from faster_whisper import WhisperModel
import io

class STTEngine:
    def __init__(self, model_size="tiny"):
        # Tiny is fastest for real-time; uses ~75MB
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_file):
        segments, _ = self.model.transcribe(audio_file, beam_size=5)
        return " ".join([s.text for s in segments]).strip()