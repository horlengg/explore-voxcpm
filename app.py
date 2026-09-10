from fastapi import FastAPI

from voxcpm_tts import VoxCPMTTS
import speech_router as SpeechRouter

app = FastAPI(title="VoxCPM TTS API")

app.include_router(SpeechRouter.router, prefix="/openai/api/v1")


@app.on_event("startup")
def load_model():
    app.state.voxcpm_engine = VoxCPMTTS()


@app.get("/health")
def health():
    return {"status": "ok"}
