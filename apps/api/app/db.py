from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4

from app.clinic import CLINIC, REASON_LABELS, STAFF_PIN
from app.schemas import CheckInBody, Ticket, TicketStatus

SEED = [
    {
        "patientName": "Ana Ruiz",
        "phone": "312-555-0190",
        "reason": "cold_flu",
        "providerId": "chen",
        "token": "A-101",
        "status": "in_visit",
    },
    {
        "patientName": "Jordan Blake",
        "phone": "773-555-0112",
        "reason": "minor_injury",
        "providerId": "hassan",
        "token": "A-102",
        "status": "waiting",
    },
    {
        "patientName": "Priya Shah",
        "phone": "847-555-0166",
        "reason": "vaccination",
        "providerId": "any",
        "token": "A-103",
        "status": "waiting",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ClinicDb:
    def __init__(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._lock = Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                token TEXT NOT NULL,
                patient_name TEXT NOT NULL,
                phone TEXT NOT NULL,
                reason TEXT NOT NULL,
                provider_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                called_at TEXT,
                notes TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )
        self._conn.commit()
        count = self._conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
        if count == 0:
            for row in SEED:
                self._insert_seed(row)
            self._set_meta("paused", "0")
            self._set_meta("pause_reason", "")
            self._set_meta("next_token", "104")
            self._conn.commit()

    def _set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )

    def _get_meta(self, key: str, default: str = "") -> str:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row else default

    def _provider_name(self, provider_id: str) -> str:
        if provider_id == "any":
            return "First available"
        for provider in CLINIC.providers:
            if provider.id == provider_id:
                return provider.name
        return "First available"

    def _active_statuses(self) -> tuple[str, ...]:
        return ("waiting", "called", "in_visit")

    def _waiting_ids(self) -> list[str]:
        rows = self._conn.execute(
            """
            SELECT id FROM tickets
            WHERE status = 'waiting'
            ORDER BY created_at ASC
            """
        ).fetchall()
        return [r["id"] for r in rows]

    def _eta(self, status: str, position: int) -> int:
        if status in {"completed", "no_show"}:
            return 0
        if status == "in_visit":
            return 8
        if status == "called":
            return 2
        paused = self._get_meta("paused") == "1"
        extra = 15 if paused else 0
        return extra + max(position, 0) * CLINIC.minutesPerVisit

    def _row_to_ticket(self, row: sqlite3.Row, waiting_ids: list[str]) -> Ticket:
        status: TicketStatus = row["status"]
        if status == "waiting":
            position = waiting_ids.index(row["id"]) if row["id"] in waiting_ids else 0
        elif status in {"called", "in_visit"}:
            position = 0
        else:
            position = -1
        return Ticket(
            id=row["id"],
            token=row["token"],
            patientName=row["patient_name"],
            phone=row["phone"],
            reason=row["reason"],
            reasonLabel=REASON_LABELS.get(row["reason"], row["reason"]),
            providerId=row["provider_id"],
            providerName=self._provider_name(row["provider_id"]),
            status=status,
            position=position,
            etaMinutes=self._eta(status, position),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
            calledAt=row["called_at"],
            notes=row["notes"] or "",
        )

    def _insert_seed(self, row: dict) -> None:
        now = _now()
        self._conn.execute(
            """
            INSERT INTO tickets
            (id, token, patient_name, phone, reason, provider_id, status, created_at, updated_at, called_at, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '')
            """,
            (
                str(uuid4()),
                row["token"],
                row["patientName"],
                row["phone"],
                row["reason"],
                row["providerId"],
                row["status"],
                now,
                now,
                now if row["status"] == "in_visit" else None,
            ),
        )

    def snapshot(self) -> dict:
        with self._lock:
            waiting_ids = self._waiting_ids()
            rows = self._conn.execute(
                "SELECT * FROM tickets ORDER BY created_at ASC"
            ).fetchall()
            tickets = [self._row_to_ticket(r, waiting_ids) for r in rows]
            paused = self._get_meta("paused") == "1"
            return {
                "paused": paused,
                "pauseReason": self._get_meta("pause_reason"),
                "waitingCount": sum(1 for t in tickets if t.status == "waiting"),
                "inVisitCount": sum(1 for t in tickets if t.status == "in_visit"),
                "completedToday": sum(1 for t in tickets if t.status == "completed"),
                "tickets": tickets,
            }

    def get_ticket(self, ticket_id: str) -> Ticket | None:
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ).fetchone()
            if not row:
                return None
            return self._row_to_ticket(row, self._waiting_ids())

    def check_in(self, body: CheckInBody) -> Ticket:
        provider_ids = {p.id for p in CLINIC.providers} | {"any"}
        if body.providerId not in provider_ids:
            raise ValueError("Unknown provider")
        with self._lock:
            n = int(self._get_meta("next_token", "101"))
            token = f"A-{n:03d}"
            self._set_meta("next_token", str(n + 1))
            now = _now()
            ticket_id = str(uuid4())
            self._conn.execute(
                """
                INSERT INTO tickets
                (id, token, patient_name, phone, reason, provider_id, status, created_at, updated_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, 'waiting', ?, ?, ?)
                """,
                (
                    ticket_id,
                    token,
                    body.patientName.strip(),
                    body.phone.strip(),
                    body.reason,
                    body.providerId,
                    now,
                    now,
                    body.notes.strip(),
                ),
            )
            self._conn.commit()
            row = self._conn.execute(
                "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
            ).fetchone()
            return self._row_to_ticket(row, self._waiting_ids())

    def _require_pin(self, pin: str) -> None:
        if pin != STAFF_PIN:
            raise PermissionError("Bad staff PIN")

    def _set_status(self, ticket_id: str, status: TicketStatus) -> Ticket:
        row = self._conn.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        if not row:
            raise KeyError(ticket_id)
        now = _now()
        called_at = row["called_at"]
        if status in {"called", "in_visit"} and not called_at:
            called_at = now
        self._conn.execute(
            """
            UPDATE tickets SET status=?, updated_at=?, called_at=?
            WHERE id=?
            """,
            (status, now, called_at, ticket_id),
        )
        self._conn.commit()
        updated = self._conn.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        return self._row_to_ticket(updated, self._waiting_ids())

    def call_next(self, pin: str, ticket_id: str | None = None) -> Ticket:
        with self._lock:
            self._require_pin(pin)
            if self._get_meta("paused") == "1":
                raise RuntimeError("Queue is paused")
            if ticket_id:
                return self._set_status(ticket_id, "called")
            waiting = self._waiting_ids()
            if not waiting:
                raise RuntimeError("No one is waiting")
            return self._set_status(waiting[0], "called")

    def start_visit(self, pin: str, ticket_id: str) -> Ticket:
        with self._lock:
            self._require_pin(pin)
            return self._set_status(ticket_id, "in_visit")

    def complete(self, pin: str, ticket_id: str) -> Ticket:
        with self._lock:
            self._require_pin(pin)
            return self._set_status(ticket_id, "completed")

    def no_show(self, pin: str, ticket_id: str) -> Ticket:
        with self._lock:
            self._require_pin(pin)
            return self._set_status(ticket_id, "no_show")

    def set_paused(self, pin: str, paused: bool, reason: str = "") -> dict:
        with self._lock:
            self._require_pin(pin)
            self._set_meta("paused", "1" if paused else "0")
            self._set_meta("pause_reason", reason if paused else "")
            self._conn.commit()
        return self.snapshot()
