import type { Ticket } from "../types";

const STATUS_COPY: Record<Ticket["status"], string> = {
  waiting: "Waiting",
  called: "Please come in",
  in_visit: "With clinician",
  completed: "Visit complete",
  no_show: "No-show",
};

export function TicketStub({ ticket, large = false }: { ticket: Ticket; large?: boolean }) {
  return (
    <article className={`stub ${large ? "stub-large" : ""}`}>
      <p className="stub-kicker">{ticket.providerName}</p>
      <p className="stub-token">{ticket.token}</p>
      <p className="stub-name">{ticket.patientName}</p>
      <p className="stub-meta">{ticket.reasonLabel}</p>
      <p className={`status status-${ticket.status}`}>{STATUS_COPY[ticket.status]}</p>
      {ticket.status === "waiting" ? (
        <p className="stub-wait">
          {ticket.position === 0
            ? "You are next"
            : `${ticket.position} ahead · ~${ticket.etaMinutes} min`}
        </p>
      ) : null}
      {ticket.status === "called" ? (
        <p className="stub-wait">Your token is up. Head to reception.</p>
      ) : null}
    </article>
  );
}
