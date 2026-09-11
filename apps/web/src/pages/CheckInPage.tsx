import { useEffect, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { checkIn, getClinic } from "../api";
import type { Clinic, VisitReason } from "../types";

const REASONS: { id: VisitReason; label: string }[] = [
  { id: "cold_flu", label: "Cold or flu symptoms" },
  { id: "minor_injury", label: "Minor injury" },
  { id: "physical", label: "Sports / school physical" },
  { id: "vaccination", label: "Vaccination" },
  { id: "prescription", label: "Prescription question" },
  { id: "other", label: "Other" },
];

export function CheckInPage() {
  const navigate = useNavigate();
  const [clinic, setClinic] = useState<Clinic | null>(null);
  const [patientName, setPatientName] = useState("");
  const [phone, setPhone] = useState("");
  const [reason, setReason] = useState<VisitReason | "">("");
  const [providerId, setProviderId] = useState("any");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    getClinic().then(setClinic).catch((err: Error) => setError(err.message));
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!patientName.trim() || !phone.trim() || !reason) {
      setError("Name, phone, and reason are required.");
      return;
    }
    setError("");
    setBusy(true);
    try {
      const ticket = await checkIn({
        patientName: patientName.trim(),
        phone: phone.trim(),
        reason,
        providerId,
        notes: notes.trim(),
      });
      navigate(`/ticket/${ticket.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Check-in failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main>
      <h1>Check in</h1>
      <p className="lede">
        You’ll get a token like the paper ones at the counter. Keep this tab open
        to watch your place in line.
      </p>

      <form className="pane form" onSubmit={onSubmit} noValidate>
        {error ? (
          <p className="form-error" role="alert">
            {error}
          </p>
        ) : null}
        <div className="field">
          <label htmlFor="patientName">Your name</label>
          <input
            id="patientName"
            value={patientName}
            onChange={(e) => setPatientName(e.target.value)}
            autoComplete="name"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="phone">Mobile number</label>
          <input
            id="phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            autoComplete="tel"
            inputMode="tel"
            required
          />
        </div>
        <div className="field">
          <label htmlFor="reason">Reason for visit</label>
          <select
            id="reason"
            value={reason}
            onChange={(e) => setReason(e.target.value as VisitReason | "")}
            required
          >
            <option value="">Select…</option>
            {REASONS.map((r) => (
              <option key={r.id} value={r.id}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="provider">Clinician</label>
          <select
            id="provider"
            value={providerId}
            onChange={(e) => setProviderId(e.target.value)}
          >
            <option value="any">First available</option>
            {clinic?.providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} — {p.specialty}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="notes">Note for the desk (optional)</label>
          <textarea
            id="notes"
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            maxLength={240}
          />
        </div>
        <button type="submit" className="primary" disabled={busy}>
          {busy ? "Checking in…" : "Get my token"}
        </button>
      </form>
    </main>
  );
}
