
import os
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional

import psutil
import soundfile as sf
from fastapi import FastAPI,HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from voxcpm import VoxCPM

from dotenv import load_dotenv

load_dotenv()


MODEL_ID = os.environ.get("VOXCPM_MODEL", "openbmb/VoxCPM2")
OUTPUT_DIR = Path(tempfile.gettempdir()) / "voxcpm_outputs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


VOICE_REF_PROMPT = {
    "en": "Received one million two hundred five thousand riel",
    "km": "ទទួលបានប្រាំបីមុឺនប្រាំពាន់ពីររយរៀល"
}

app = FastAPI(title="VoxCPM TTS API")
model: Optional[VoxCPM] = None


@app.on_event("startup")
def load_model():
    global model
    print(f"Loading {MODEL_ID} ...")
    model = VoxCPM.from_pretrained(MODEL_ID, load_denoiser=False)
    print("Model loaded.")





class TTSCloneRequest(BaseModel):
    text: str


@app.post("/tts/{gender}/{lang}/generate")
async def tts_clone(gender: str,lang : str,payload: TTSCloneRequest):


    if model is None:
        raise HTTPException(503, "Model still loading")

    gender_clean = gender.lower() if isinstance(gender, str) else ""
    lang_clean = lang.lower() if isinstance(lang, str) else ""

    if gender_clean not in ["male", "female"]:
        raise HTTPException(
            status_code=422, detail="Invalid gender! Must be 'male' or 'female'."
        )

    if lang_clean not in ["en", "km"]:
            raise HTTPException(
                status_code=422, detail="Invalid language! Must be 'en' or 'km'."
            )

    start = time.perf_counter()

    gen_kwargs = dict(
        text=payload.text,
        cfg_value= 2.0,
        inference_timesteps=10
    )

    ref_voice_path = f"./reference/{lang_clean}/{gender_clean}-reference-voice.wav"

    gen_kwargs["reference_wav_path"] = ref_voice_path
    gen_kwargs["prompt_wav_path"] = ref_voice_path
    gen_kwargs["prompt_text"] = VOICE_REF_PROMPT[lang_clean]

    wav = model.generate(**gen_kwargs)
    duration = time.perf_counter() - start

    out_path = OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
    sf.write(out_path, wav, model.tts_model.sample_rate)

    return FileResponse(
        out_path,
        media_type="audio/wav",
        filename="sound.wav",
        headers={"X-Inference-Time": f"{duration:.3f}"},
    )


@app.get("/health/memory")
def memory_usage():
    process = psutil.Process(os.getpid())
    mem = process.memory_info()
    return {
        "rss_mb": mem.rss / 1024 / 1024,   # actual RAM used
        "vms_mb": mem.vms / 1024 / 1024,   # virtual memory
    }

@app.get("/health")
def health():
    return {"status": "ok" if model is not None else "loading"}