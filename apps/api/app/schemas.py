from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

VisitReason = Literal[
    "cold_flu",
    "minor_injury",
    "physical",
    "vaccination",
    "prescription",
    "other",
]

TicketStatus = Literal["waiting", "called", "in_visit", "completed", "no_show"]


class Provider(BaseModel):
    id: str
    name: str
    specialty: str
    room: str


class ClinicHours(BaseModel):
    weekday: str
    open: str
    close: str


class Clinic(BaseModel):
    name: str
    address: str
    phone: str
    parking: str
    insuranceNotes: str
    whatToBring: list[str]
    hours: list[ClinicHours]
    providers: list[Provider]
    minutesPerVisit: int
    staffPinHint: str


class Ticket(BaseModel):
    id: str
    token: str
    patientName: str
    phone: str
    reason: VisitReason
    reasonLabel: str
    providerId: str
    providerName: str
    status: TicketStatus
    position: int
    etaMinutes: int
    createdAt: str
    updatedAt: str
    calledAt: str | None = None
    notes: str = ""


class QueueSnapshot(BaseModel):
    paused: bool
    pauseReason: str
    waitingCount: int
    inVisitCount: int
    completedToday: int
    tickets: list[Ticket]


class CheckInBody(BaseModel):
    patientName: str = Field(min_length=1, max_length=80)
    phone: str = Field(min_length=7, max_length=32)
    reason: VisitReason
    providerId: str = "any"
    notes: str = Field(default="", max_length=240)


class StaffActionBody(BaseModel):
    pin: str = Field(min_length=4, max_length=12)


class PauseBody(StaffActionBody):
    reason: str = Field(default="Short break", max_length=120)


class DeskChatBody(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    ticketId: str | None = None


class DeskChatReply(BaseModel):
    reply: str
    disclaimer: str
    emergency: bool = False
