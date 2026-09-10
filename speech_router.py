import os
import traceback
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request, Response
from utils.transaction_amount import validate_trx_request, build_tts_text

from speech_request import SpeechRequest,SpeechTextRequest


router = APIRouter(prefix="/speech", tags=["speech"])


@router.post("/generate")
async def generate_trx_speech(
    request: SpeechRequest,
    http_request: Request,
    background_tasks: BackgroundTasks,
):
    validate_trx_request(request=request)

    file_saved_path = request.voice.get_saved_path(
        request.language, request.currency, request.amount
    )
    if os.path.isfile(file_saved_path):
        with open(file_saved_path, "rb") as f:
            cached_bytes = f.read()
        return Response(content=cached_bytes, media_type="audio/wav")

    try:
        voxcpm_engine = http_request.app.state.voxcpm_engine
        raw_bytes = await voxcpm_engine.generate(request=request)

        background_tasks.add_task(_save_safely, file_saved_path, raw_bytes)

        return Response(content=raw_bytes, media_type="audio/wav")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


async def _save_safely(file_saved_path: str, raw_bytes: bytes):
    try:
        os.makedirs(os.path.dirname(file_saved_path), exist_ok=True)
        with open(file_saved_path, "wb") as f:
            f.write(raw_bytes)
        print(f"Saved file to {file_saved_path}")
    except Exception:
        traceback.print_exc()




@router.post("/speak")
async def speak_text(
    request: SpeechTextRequest,
    http_request: Request,
):
    print("Speaking content =", request.content)

    try:
        voxcpm_engine = http_request.app.state.voxcpm_engine
        raw_bytes = await voxcpm_engine.generate_text(
            language=request.language,
            voice=request.voice,
            content=request.content,
        )

        return Response(content=raw_bytes, media_type="audio/wav")

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))