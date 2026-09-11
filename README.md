# PulseLine

Walk-in clinic **digital queue** and **front-desk assistant** for a demo urgent-care site (PulseLine Urgent Care, Chicago). Patients check in from a phone, keep a live token, and ask hours/parking/wait questions. Staff call the next patient, start a visit, mark complete or no-show, and pause the line.

This is **not medical advice** and **not an ER**. Emergencies go to 911.

```
Browser (React) → FastAPI → SQLite
```

Same shape as [CaseDraft](https://github.com/suryat9988/casedraft): structured intake, stub “AI” behind an API, human staff still run the queue.

## Run locally (two terminals)

API:

```bash
cd apps/api
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

UI:

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` to port 8000.

Staff PIN for the board: **2468** (demo only).

Seeded tokens so the board is not empty: Ana Ruiz is in visit (`A-101`); Jordan Blake and Priya Shah are waiting.

## Docker Compose

```bash
docker compose up --build
```

Open http://localhost:8080

## Tests / CI

```bash
cd apps/api && pytest
cd apps/web && npm run build
```

GitHub Actions runs both on pull requests (`.github/workflows/ci.yml`).

## What it does

| Role | Flow |
| --- | --- |
| Patient | Check in → token stub with position and ETA → live refresh → chat with desk |
| Staff | PIN gate → call next / call a specific token → start visit → complete or no-show → pause/resume |
| Desk bot | Hours, wait, parking, insurance, what to bring. Symptom questions are deflected. “Chest pain” / can’t breathe routes to 911. |

Wait time is a simple `people ahead × 12 minutes` (clinic `minutesPerVisit`). No PHI store beyond the demo names and phone numbers you type.

## Repo note

This Cloud Agent run was started against `suryat9988/ML-Project` (an old VS Code Go sample). The intended GitHub repo is [`suryat9988/PulseLine`](https://github.com/suryat9988/PulseLine), which was empty at the time. Copy this tree there, or start a new agent with PulseLine selected, if you want the history on that remote. The original Go hello-world files are left in place.
