import { useEffect, useState } from "react";
import {
  callNext,
  callTicket,
  completeVisit,
  getQueue,
  markNoShow,
  pauseQueue,
  resumeQueue,
  startVisit,
} from "../api";
import { TicketStub } from "../components/TicketStub";
import type { QueueSnapshot, Ticket } from "../types";

const PIN_KEY = "pulseline-staff-pin";

export function StaffPage() {
  const [pin, setPin] = useState(() => sessionStorage.getItem(PIN_KEY) || "");
  const [unlocked, setUnlocked] = useState(() => Boolean(sessionStorage.getItem(PIN_KEY)));
  const [queue, setQueue] = useState<QueueSnapshot | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!unlocked) return;
    let cancelled = false;
    async function load() {
      try {
        const next = await getQueue();
        if (!cancelled) {
          setQueue(next);
          setError("");
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Queue failed");
        }
      }
    }
    load();
    const timer = window.setInterval(load, 2500);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [unlocked]);

  function unlock() {
    if (pin.trim().length < 4) {
      setError("Enter the staff PIN.");
      return;
    }
    sessionStorage.setItem(PIN_KEY, pin.trim());
    setUnlocked(true);
    setError("");
  }

  async function run(action: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    try {
      await action();
      setQueue(await getQueue());
    } catch (err) {
      const message = err instanceof Error ? err.message : "Action failed";
      setError(message);
      if (message.toLowerCase().includes("pin")) {
        sessionStorage.removeItem(PIN_KEY);
        setUnlocked(false);
      }
    } finally {
      setBusy(false);
    }
  }

  if (!unlocked) {
    return (
      <main>
        <h1>Staff board</h1>
        <p className="lede">Demo PIN is 2468. This is not real authentication.</p>
        <div className="pane form">
          {error ? (
            <p className="form-error" role="alert">
              {error}
            </p>
          ) : null}
          <div className="field">
            <label htmlFor="pin">Staff PIN</label>
            <input
              id="pin"
              type="password"
              value={pin}
              onChange={(e) => setPin(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") unlock();
              }}
              autoComplete="off"
            />
          </div>
          <button type="button" className="primary" onClick={unlock}>
            Open board
          </button>
        </div>
      </main>
    );
  }

  const waiting = queue?.tickets.filter((t) => t.status === "waiting") ?? [];
  const active =
    queue?.tickets.filter((t) => t.status === "called" || t.status === "in_visit") ?? [];

  return (
    <main>
      <div className="case-title-row">
        <h1>Staff board</h1>
        {queue?.paused ? <span className="status status-paused">Paused</span> : null}
      </div>
      {queue?.paused && queue.pauseReason ? (
        <p className="banner banner-warn">Line paused: {queue.pauseReason}</p>
      ) : null}
      {error ? (
        <p className="form-error" role="alert">
          {error}
        </p>
      ) : null}

      <div className="actions">
        <button
          type="button"
          className="primary"
          disabled={busy || queue?.paused}
          onClick={() => run(() => callNext(pin))}
        >
          Call next
        </button>
        {queue?.paused ? (
          <button type="button" disabled={busy} onClick={() => run(() => resumeQueue(pin))}>
            Resume line
          </button>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={() => run(() => pauseQueue(pin, "Short break"))}
          >
            Pause line
          </button>
        )}
      </div>

      <section>
        <h2>Rooms</h2>
        {active.length === 0 ? (
          <p className="hint">No one called yet.</p>
        ) : (
          <div className="stub-row">
            {active.map((t) => (
              <StaffTicket key={t.id} ticket={t} pin={pin} busy={busy} run={run} />
            ))}
          </div>
        )}
      </section>

      <section>
        <h2>Waiting ({waiting.length})</h2>
        {waiting.length === 0 ? (
          <p className="hint">Queue is empty.</p>
        ) : (
          <table className="case-table">
            <thead>
              <tr>
                <th>Token</th>
                <th>Patient</th>
                <th>Reason</th>
                <th>Clinician</th>
                <th>ETA</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {waiting.map((t) => (
                <tr key={t.id}>
                  <td>{t.token}</td>
                  <td>{t.patientName}</td>
                  <td>{t.reasonLabel}</td>
                  <td>{t.providerName}</td>
                  <td>~{t.etaMinutes} min</td>
                  <td>
                    <button
                      type="button"
                      disabled={busy || queue?.paused}
                      onClick={() => run(() => callTicket(t.id, pin))}
                    >
                      Call
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

function StaffTicket({
  ticket,
  pin,
  busy,
  run,
}: {
  ticket: Ticket;
  pin: string;
  busy: boolean;
  run: (action: () => Promise<unknown>) => Promise<void>;
}) {
  return (
    <div>
      <TicketStub ticket={ticket} />
      <div className="actions">
        {ticket.status === "called" ? (
          <button
            type="button"
            className="primary"
            disabled={busy}
            onClick={() => run(() => startVisit(ticket.id, pin))}
          >
            Start visit
          </button>
        ) : null}
        <button
          type="button"
          disabled={busy}
          onClick={() => run(() => completeVisit(ticket.id, pin))}
        >
          Complete
        </button>
        <button
          type="button"
          className="danger"
          disabled={busy}
          onClick={() => run(() => markNoShow(ticket.id, pin))}
        >
          No-show
        </button>
      </div>
    </div>
  );
}
