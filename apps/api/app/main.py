from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.clinic import CLINIC
from app.db import ClinicDb
from app.desk import reply
from app.schemas import (
    CheckInBody,
    DeskChatBody,
    PauseBody,
    QueueSnapshot,
    StaffActionBody,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("pulseline")

DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/pulseline.db")
db = ClinicDb(DATABASE_PATH)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    log.info("PulseLine API db=%s", DATABASE_PATH)
    yield


app = FastAPI(title="PulseLine API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _http_from(exc: Exception) -> HTTPException:
    if isinstance(exc, PermissionError):
        return HTTPException(403, str(exc))
    if isinstance(exc, KeyError):
        return HTTPException(404, "Ticket not found")
    if isinstance(exc, ValueError):
        return HTTPException(400, str(exc))
    if isinstance(exc, RuntimeError):
        return HTTPException(409, str(exc))
    return HTTPException(500, "Unexpected error")


@app.get("/api/health")
def health():
    return {"ok": True, "service": "pulseline"}


@app.get("/api/clinic")
def clinic():
    return CLINIC


@app.get("/api/queue")
def queue() -> QueueSnapshot:
    return QueueSnapshot.model_validate(db.snapshot())


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    ticket = db.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(404, "Ticket not found")
    return ticket


@app.post("/api/check-in", status_code=201)
def check_in(body: CheckInBody):
    try:
        return db.check_in(body)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/queue/call-next")
def call_next(body: StaffActionBody):
    try:
        return db.call_next(body.pin)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/tickets/{ticket_id}/call")
def call_ticket(ticket_id: str, body: StaffActionBody):
    try:
        return db.call_next(body.pin, ticket_id)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/tickets/{ticket_id}/start")
def start_visit(ticket_id: str, body: StaffActionBody):
    try:
        return db.start_visit(body.pin, ticket_id)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/tickets/{ticket_id}/complete")
def complete(ticket_id: str, body: StaffActionBody):
    try:
        return db.complete(body.pin, ticket_id)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/tickets/{ticket_id}/no-show")
def no_show(ticket_id: str, body: StaffActionBody):
    try:
        return db.no_show(body.pin, ticket_id)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/queue/pause")
def pause(body: PauseBody):
    try:
        return db.set_paused(body.pin, True, body.reason)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/queue/resume")
def resume(body: StaffActionBody):
    try:
        return db.set_paused(body.pin, False)
    except Exception as exc:
        raise _http_from(exc) from exc


@app.post("/api/desk/chat")
def desk_chat(body: DeskChatBody):
    snapshot = QueueSnapshot.model_validate(db.snapshot())
    ticket = db.get_ticket(body.ticketId) if body.ticketId else None
    return reply(body.message, snapshot, ticket)
