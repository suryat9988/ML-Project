import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getClinic, getQueue } from "../api";
import { DeskChat } from "../components/DeskChat";
import type { Clinic, QueueSnapshot } from "../types";

export function HomePage() {
  const [clinic, setClinic] = useState<Clinic | null>(null);
  const [queue, setQueue] = useState<QueueSnapshot | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getClinic(), getQueue()])
      .then(([c, q]) => {
        setClinic(c);
        setQueue(q);
      })
      .catch((err: Error) =>
        setError(
          err.message ||
            "Cannot reach the API. Start it with: cd apps/api && uvicorn app.main:app --reload --port 8000",
        ),
      );
  }, []);

  return (
    <main>
      {error ? (
        <p className="form-error" role="alert">
          {error}
        </p>
      ) : null}

      <section className="hero">
        <p className="eyebrow">Chicago walk-in clinic</p>
        <h1>Skip the paper ticket. Keep your place in line.</h1>
        <p className="lede">
          PulseLine is the front desk for a demo urgent-care clinic: check in from
          your phone, watch the queue, and ask hours or parking questions. A
          clinician still sees you in order — this is not a diagnosis tool.
        </p>
        <div className="hero-actions">
          <Link to="/check-in" className="button-link primary">
            Check in
          </Link>
          <Link to="/staff" className="button-link">
            Staff board
          </Link>
        </div>
      </section>

      <section className="stats" aria-label="Live queue">
        <div>
          <strong>{queue ? queue.waitingCount : "—"}</strong>
          <span>Waiting</span>
        </div>
        <div>
          <strong>{queue ? queue.inVisitCount : "—"}</strong>
          <span>In visit</span>
        </div>
        <div>
          <strong>{queue ? queue.completedToday : "—"}</strong>
          <span>Seen today</span>
        </div>
        <div>
          <strong>{queue?.paused ? "Paused" : "Open"}</strong>
          <span>Line status</span>
        </div>
      </section>

      {clinic ? (
        <div className="split">
          <section className="pane">
            <h2>Today at {clinic.name}</h2>
            <address className="plain">
              {clinic.address}
              <br />
              {clinic.phone}
            </address>
            <ul className="hours">
              {clinic.hours.map((h) => (
                <li key={h.weekday}>
                  <span>{h.weekday}</span>
                  <span>
                    {h.open}–{h.close}
                  </span>
                </li>
              ))}
            </ul>
            <h3>Bring with you</h3>
            <ul>
              {clinic.whatToBring.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </section>
          <section className="pane">
            <h2>Who is on</h2>
            <ul className="providers">
              {clinic.providers.map((p) => (
                <li key={p.id}>
                  <strong>{p.name}</strong>
                  <span>
                    {p.specialty} · {p.room}
                  </span>
                </li>
              ))}
            </ul>
            <p className="hint">{clinic.insuranceNotes}</p>
          </section>
        </div>
      ) : null}

      <DeskChat />
    </main>
  );
}
