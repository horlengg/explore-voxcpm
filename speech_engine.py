from pathlib import Path
import asyncio
import tempfile
import time
from typing import Optional
import uuid

from voxcpm import VoxCPM
import soundfile as sf

from utils.transaction_amount import build_tts_text
from speech_request import SpeechRequest


class SpeechEngine :

    model: Optional[VoxCPM] = None
    OUTPUT_DIR = Path(tempfile.gettempdir()) / "voxcpm_outputs"

    def __init__(self, model_name: str = "openbmb/VoxCPM2"):
        print(f"Start load {model_name} ...")
        start = time.perf_counter()

        self.model = VoxCPM.from_pretrained(model_name, load_denoiser=False)
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        duration = time.perf_counter() - start
        print(f"Load model successfully! Took {duration:.3f}s")

    async def generate(self, request: SpeechRequest) -> bytes:
        return await asyncio.to_thread(self._generate_sync, request)

    def _generate_sync(self, request: SpeechRequest) -> bytes:
        start = time.perf_counter()

        speak_content = build_tts_text(request=request)
        print("Contents = ", speak_content)

        reference_voice_path = request.voice.get_reference_path(request.language)

        gen_kwargs = dict(
            text=speak_content,
            cfg_value=2.0,
            inference_timesteps=10,
            reference_wav_path=reference_voice_path,
            prompt_wav_path=reference_voice_path,
            prompt_text=request.voice.get_reference_prompt(request.language),
        )

        wav = self.model.generate(**gen_kwargs)
        duration = time.perf_counter() - start
        print(f"Inference took {duration:.3f}s")

        out_path = self.OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
        sf.write(out_path, wav, self.model.tts_model.sample_rate)

        raw_bytes = out_path.read_bytes()
        out_path.unlink(missing_ok=True)  # cleanup temp file
        return raw_bytes


    # For generate voice directly
    async def generate_text(self, language, voice, content: str) -> bytes:
        return await asyncio.to_thread(self._generate_text_sync, language, voice, content)

    def _generate_text_sync(self, language, voice, content: str) -> bytes:
        start = time.perf_counter()
        print("Contents = ", content)

        reference_voice_path = voice.get_reference_path(language)

        gen_kwargs = dict(
            text=content,
            cfg_value=2.0,
            inference_timesteps=10,
            reference_wav_path=reference_voice_path,
            prompt_wav_path=reference_voice_path,
            prompt_text=voice.get_reference_prompt(language),
        )

        wav = self.model.generate(**gen_kwargs)
        duration = time.perf_counter() - start
        print(f"Inference took {duration:.3f}s")

        out_path = self.OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
        sf.write(out_path, wav, self.model.tts_model.sample_rate)

        raw_bytes = out_path.read_bytes()
        out_path.unlink(missing_ok=True)
        return raw_bytes