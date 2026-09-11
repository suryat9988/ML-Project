import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getTicket } from "../api";
import { DeskChat } from "../components/DeskChat";
import { TicketStub } from "../components/TicketStub";
import type { Ticket } from "../types";

export function TicketPage() {
  const { id } = useParams();
  const [ticket, setTicket] = useState<Ticket | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    async function load() {
      try {
        const next = await getTicket(id!);
        if (!cancelled) setTicket(next);
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Ticket not found");
        }
      }
    }
    load();
    const timer = window.setInterval(load, 3000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [id]);

  return (
    <main>
      <p className="crumb">
        <Link to="/">Home</Link> · your token
      </p>
      {error ? (
        <p className="form-error" role="alert">
          {error}
        </p>
      ) : null}
      {ticket ? (
        <>
          <TicketStub ticket={ticket} large />
          <p className="hint">
            This page refreshes every few seconds. When the status says “Please
            come in”, walk to reception.
          </p>
          <DeskChat ticketId={ticket.id} />
        </>
      ) : (
        <p>Loading your token…</p>
      )}
    </main>
  );
}
