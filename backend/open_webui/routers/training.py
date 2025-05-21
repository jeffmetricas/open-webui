import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Request

from open_webui.utils.auth import get_verified_user
from open_webui.env import DATA_DIR, SRC_LOG_LEVELS

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MAIN"])

router = APIRouter()

TRAINING_DIR = Path(DATA_DIR) / "training"
TRAINING_DIR.mkdir(parents=True, exist_ok=True)


def _log_payload(filename: str, payload: dict) -> None:
    try:
        with open(TRAINING_DIR / filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload) + "\n")
    except Exception as e:
        log.error(f"Failed to write training payload: {e}")


@router.post("/document")
async def training_document(request: Request, user=Depends(get_verified_user)):
    data: Any = await request.json()
    log.info("Received document training payload")
    _log_payload("document.log", {"user_id": user.id, "payload": data})
    return {"status": "received"}


@router.post("/chat")
async def training_chat(request: Request, user=Depends(get_verified_user)):
    data: Any = await request.json()
    log.info("Received chat training payload")
    _log_payload("chat.log", {"user_id": user.id, "payload": data})
    return {"status": "received"}


@router.post("/save")
async def training_save(request: Request, user=Depends(get_verified_user)):
    data: Any = await request.json()
    log.info("Received save training payload")
    _log_payload("save.log", {"user_id": user.id, "payload": data})
    return {"status": "saved"}
