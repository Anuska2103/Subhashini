import edge_tts
import asyncio

class TTSEngine:
    async def generate(self, text, voice="hi-IN-SwaraNeural"):
        communicate = edge_tts.Communicate(text, voice)
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data