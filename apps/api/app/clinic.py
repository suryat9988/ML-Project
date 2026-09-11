from __future__ import annotations

from app.schemas import Clinic, ClinicHours, Provider

REASON_LABELS = {
    "cold_flu": "Cold or flu symptoms",
    "minor_injury": "Minor injury",
    "physical": "Sports / school physical",
    "vaccination": "Vaccination",
    "prescription": "Prescription question",
    "other": "Other",
}

STAFF_PIN = "2468"

CLINIC = Clinic(
    name="PulseLine Urgent Care",
    address="1847 N Milwaukee Ave, Chicago, IL 60647",
    phone="(312) 555-0148",
    parking="Lot behind the building. Street parking on Milwaukee after 6pm.",
    insuranceNotes=(
        "We take most commercial plans and Medicare. Bring your card. "
        "Self-pay visit starts at $89."
    ),
    whatToBring=[
        "Photo ID",
        "Insurance card (if you have one)",
        "Medication list",
        "A payment method for copay or self-pay",
    ],
    hours=[
        ClinicHours(weekday="Monday–Friday", open="08:00", close="20:00"),
        ClinicHours(weekday="Saturday", open="09:00", close="16:00"),
        ClinicHours(weekday="Sunday", open="10:00", close="14:00"),
    ],
    providers=[
        Provider(
            id="chen",
            name="Dr. Maya Chen",
            specialty="Family medicine",
            room="Room 1",
        ),
        Provider(
            id="hassan",
            name="Dr. Omar Hassan",
            specialty="Urgent care",
            room="Room 2",
        ),
    ],
    minutesPerVisit=12,
    staffPinHint="Demo staff PIN is 2468",
)
