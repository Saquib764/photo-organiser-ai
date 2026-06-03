"""WebSocket endpoints for live workspace status."""

import asyncio
import json
import logging
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.config import settings
from app.services.pipeline_runner import (
    handle_rerun_analysis,
    handle_rerun_categorisation,
    handle_rerun_face_extraction,
    handle_start_analysis,
    handle_start_categorisation,
    handle_start_face_extraction,
    handle_start_palette_extraction,
    handle_start_processing,
)
from app.services.status import build_workspace_status

logger = logging.getLogger(__name__)

router = APIRouter()


async def _safe_close(websocket: WebSocket, *, code: int) -> None:
    try:
        await websocket.close(code=code)
    except (WebSocketDisconnect, RuntimeError):
        pass


async def send_status(
    websocket: WebSocket,
    *,
    reason: str,
    discover: bool = False,
) -> None:
    client = websocket.client
    client_label = f"{client.host}:{client.port}" if client else "unknown"
    started = time.perf_counter()
    logger.info(
        "Building workspace status for %s (reason=%s)",
        client_label,
        reason,
    )
    try:
        status = await asyncio.to_thread(
            build_workspace_status,
            settings.workspace_root,
            discover=discover,
        )
    except Exception:
        logger.exception(
            "Failed to build workspace status for %s (reason=%s)",
            client_label,
            reason,
        )
        raise

    build_ms = (time.perf_counter() - started) * 1000
    logger.info(
        "Workspace status built for %s in %.0fms (reason=%s, raw=%d, processed=%d, busy=%s)",
        client_label,
        build_ms,
        reason,
        status.total_images_raw,
        status.total_images_processed,
        status.processing_busy,
    )

    payload = status.model_dump(mode="json")
    try:
        await websocket.send_json({"type": "status", "payload": payload})
    except WebSocketDisconnect:
        logger.info(
            "Client %s disconnected before status could be sent (reason=%s)",
            client_label,
            reason,
        )
        raise
    logger.info(
        "Sent status to %s (reason=%s, payload_bytes≈%d)",
        client_label,
        reason,
        len(json.dumps(payload)),
    )


@router.websocket("/ws")
async def workspace_status_ws(websocket: WebSocket) -> None:
    origin = websocket.headers.get("origin")
    client = websocket.client
    client_label = f"{client.host}:{client.port}" if client else "unknown"

    if origin and origin not in settings.cors_origins:
        logger.warning(
            "WebSocket rejected for %s: origin %r not in cors_origins",
            client_label,
            origin,
        )
        await websocket.close(code=1008)
        return

    await websocket.accept()
    logger.info(
        "WebSocket connected: %s origin=%r",
        client_label,
        origin,
    )

    try:
        await send_status(websocket, reason="connect", discover=True)
    except WebSocketDisconnect:
        logger.info(
            "WebSocket disconnected during initial status for %s",
            client_label,
        )
        return
    except Exception:
        logger.exception("Initial status send failed for %s", client_label)
        await _safe_close(websocket, code=1011)
        return

    try:
        while True:
            raw = await websocket.receive_text()
            logger.debug("WebSocket message from %s: %s", client_label, raw[:200])

            try:
                message = json.loads(raw)
            except json.JSONDecodeError:
                logger.debug("Ignoring non-JSON WebSocket message from %s", client_label)
                continue

            msg_type = message.get("type")
            logger.info("WebSocket command from %s: type=%r", client_label, msg_type)

            try:
                if msg_type == "request_status":
                    discover = bool(message.get("discover", False))
                    await send_status(
                        websocket,
                        reason="request_status",
                        discover=discover,
                    )
                elif msg_type == "start_processing":
                    await handle_start_processing(settings.workspace_root)
                    await send_status(websocket, reason="after_start_processing")
                elif msg_type == "start_face_extraction":
                    await handle_start_face_extraction(settings.workspace_root)
                    await send_status(websocket, reason="after_start_face_extraction")
                elif msg_type == "rerun_face_extraction":
                    await handle_rerun_face_extraction(settings.workspace_root)
                    await send_status(websocket, reason="after_rerun_face_extraction")
                elif msg_type == "start_palette_extraction":
                    await handle_start_palette_extraction(settings.workspace_root)
                    await send_status(
                        websocket,
                        reason="after_start_palette_extraction",
                    )
                elif msg_type == "start_analysis":
                    await handle_start_analysis(settings.workspace_root)
                    await send_status(websocket, reason="after_start_analysis")
                elif msg_type == "rerun_analysis":
                    await handle_rerun_analysis(settings.workspace_root)
                    await send_status(websocket, reason="after_rerun_analysis")
                elif msg_type == "start_categorisation":
                    await handle_start_categorisation(settings.workspace_root)
                    await send_status(websocket, reason="after_start_categorisation")
                elif msg_type == "rerun_categorisation":
                    await handle_rerun_categorisation(settings.workspace_root)
                    await send_status(websocket, reason="after_rerun_categorisation")
                else:
                    logger.debug(
                        "Ignoring unknown WebSocket message type %r from %s",
                        msg_type,
                        client_label,
                    )
            except WebSocketDisconnect:
                raise
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", client_label)
