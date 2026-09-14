from fastapi import FastAPI

from speech_engine import SpeechEngine
import speech_router as SpeechRouter

app = FastAPI(title="VoxCPM TTS API")

app.include_router(SpeechRouter.router, prefix="/openai/api/v1")


@app.on_event("startup")
def load_model():
    app.state.voxcpm_engine = SpeechEngine()


@app.get("/health")
def health():
    return {"status": "ok"}
