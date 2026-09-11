from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PIN = "2468"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "test.db"))
    for name in list(sys.modules):
        if name == "app" or name.startswith("app."):
            del sys.modules[name]
    from app.main import app

    return TestClient(app)


def test_health(client: TestClient):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["service"] == "pulseline"


def test_clinic_has_providers(client: TestClient):
    res = client.get("/api/clinic")
    assert res.status_code == 200
    body = res.json()
    assert body["name"] == "PulseLine Urgent Care"
    assert len(body["providers"]) == 2


def test_queue_seeds_waiting_patients(client: TestClient):
    res = client.get("/api/queue")
    assert res.status_code == 200
    body = res.json()
    tokens = {t["token"] for t in body["tickets"]}
    assert {"A-101", "A-102", "A-103"} <= tokens
    assert body["waitingCount"] >= 2


def test_check_in_assigns_next_token_and_position(client: TestClient):
    res = client.post(
        "/api/check-in",
        json={
            "patientName": "Sam Lee",
            "phone": "312-555-0100",
            "reason": "physical",
            "providerId": "chen",
        },
    )
    assert res.status_code == 201
    ticket = res.json()
    assert ticket["token"] == "A-104"
    assert ticket["status"] == "waiting"
    assert ticket["patientName"] == "Sam Lee"
    assert ticket["position"] >= 0

    fetched = client.get(f"/api/tickets/{ticket['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["token"] == "A-104"


def test_staff_pin_required(client: TestClient):
    res = client.post("/api/queue/call-next", json={"pin": "0000"})
    assert res.status_code == 403


def test_call_next_then_complete(client: TestClient):
    nxt = client.post("/api/queue/call-next", json={"pin": PIN})
    assert nxt.status_code == 200
    ticket = nxt.json()
    assert ticket["status"] == "called"
    assert ticket["token"] == "A-102"

    start = client.post(f"/api/tickets/{ticket['id']}/start", json={"pin": PIN})
    assert start.json()["status"] == "in_visit"

    done = client.post(f"/api/tickets/{ticket['id']}/complete", json={"pin": PIN})
    assert done.json()["status"] == "completed"


def test_pause_blocks_call_next(client: TestClient):
    paused = client.post(
        "/api/queue/pause", json={"pin": PIN, "reason": "Lunch"}
    )
    assert paused.status_code == 200
    assert paused.json()["paused"] is True
    blocked = client.post("/api/queue/call-next", json={"pin": PIN})
    assert blocked.status_code == 409
    resumed = client.post("/api/queue/resume", json={"pin": PIN})
    assert resumed.json()["paused"] is False


def test_desk_chat_hours_and_emergency(client: TestClient):
    hours = client.post("/api/desk/chat", json={"message": "What time do you close?"})
    assert hours.status_code == 200
    assert "20:00" in hours.json()["reply"]
    assert hours.json()["emergency"] is False

    em = client.post(
        "/api/desk/chat", json={"message": "I have chest pain and can't breathe"}
    )
    assert em.status_code == 200
    assert em.json()["emergency"] is True
    assert "911" in em.json()["reply"]
