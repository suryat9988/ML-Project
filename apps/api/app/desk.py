from __future__ import annotations

import re

from app.clinic import CLINIC, REASON_LABELS
from app.schemas import DeskChatReply, QueueSnapshot, Ticket

DISCLAIMER = (
    "PulseLine is a clinic front desk, not a clinician. "
    "This is not medical advice and not a diagnosis."
)

EMERGENCY_RE = re.compile(
    r"\b(chest pain|can't breathe|cannot breathe|stroke|unconscious|"
    r"severe bleeding|suicidal|overdose|911)\b",
    re.I,
)


def reply(message: str, snapshot: QueueSnapshot, ticket: Ticket | None) -> DeskChatReply:
    text = message.strip()
    if EMERGENCY_RE.search(text):
        return DeskChatReply(
            reply=(
                "If this is an emergency, hang up and call 911 or go to the nearest ER. "
                "PulseLine Urgent Care is not an emergency department."
            ),
            disclaimer=DISCLAIMER,
            emergency=True,
        )

    lower = text.lower()
    hours = "; ".join(f"{h.weekday} {h.open}–{h.close}" for h in CLINIC.hours)
    wait = (
        "The line is paused right now — check back in a few minutes."
        if snapshot.paused
        else (
            f"{snapshot.waitingCount} patient(s) waiting. "
            "Typical visit is about "
            f"{CLINIC.minutesPerVisit} minutes once you are called."
        )
    )
    if ticket and ticket.status in {"waiting", "called"}:
        wait = (
            f"You are {ticket.token}, currently {ticket.status.replace('_', ' ')}. "
            f"About {ticket.position} ahead of you, ~{ticket.etaMinutes} min."
        )

    if any(k in lower for k in ("hour", "open", "close", "today")):
        body = f"{CLINIC.name} hours: {hours}. Phone {CLINIC.phone}."
    elif any(k in lower for k in ("wait", "how long", "queue", "line", "token")):
        body = wait
    elif any(k in lower for k in ("insurance", "copay", "self-pay", "cost", "price")):
        body = CLINIC.insuranceNotes
    elif any(k in lower for k in ("bring", "need to bring", "id", "card")):
        body = "Please bring: " + "; ".join(CLINIC.whatToBring) + "."
    elif any(k in lower for k in ("park", "parking", "lot")):
        body = CLINIC.parking
    elif any(k in lower for k in ("address", "where", "location", "direction")):
        body = f"We are at {CLINIC.address}. {CLINIC.parking}"
    elif any(k in lower for k in ("doctor", "provider", "who is on")):
        people = ", ".join(f"{p.name} ({p.specialty}, {p.room})" for p in CLINIC.providers)
        body = f"Today's providers: {people}."
    elif any(k in lower for k in ("refill", "prescription", "rx")):
        body = (
            "For prescription questions, check in with reason "
            f"“{REASON_LABELS['prescription']}”. "
            "Bring the bottle or the medication name. We cannot refill controlled "
            "substances without the prescribing clinician."
        )
    elif any(k in lower for k in ("fever", "cough", "pain", "symptom", "sick", "hurt")):
        body = (
            "I cannot assess symptoms. If you feel unsafe, call 911. "
            "Otherwise check in at the kiosk — a clinician will see you in order."
        )
    else:
        body = (
            f"Hi — I'm the PulseLine front desk. {wait} "
            "I can help with hours, parking, what to bring, insurance, and your ticket."
        )

    return DeskChatReply(reply=body, disclaimer=DISCLAIMER, emergency=False)
