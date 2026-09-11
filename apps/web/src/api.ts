import type { CheckInInput, Clinic, DeskReply, QueueSnapshot, Ticket } from "./types";

async function parse<T>(res: Response): Promise<T> {
  const text = await res.text();
  let body: unknown = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = text;
  }
  if (!res.ok) {
    const detail =
      typeof body === "object" && body && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : res.statusText;
    throw new Error(detail);
  }
  return body as T;
}

export function getClinic() {
  return fetch("/api/clinic").then((r) => parse<Clinic>(r));
}

export function getQueue() {
  return fetch("/api/queue").then((r) => parse<QueueSnapshot>(r));
}

export function getTicket(id: string) {
  return fetch(`/api/tickets/${id}`).then((r) => parse<Ticket>(r));
}

export function checkIn(input: CheckInInput) {
  return fetch("/api/check-in", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  }).then((r) => parse<Ticket>(r));
}

function staffPost<T>(url: string, pin: string, extra: Record<string, string> = {}) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pin, ...extra }),
  }).then((r) => parse<T>(r));
}

export function callNext(pin: string) {
  return staffPost<Ticket>("/api/queue/call-next", pin);
}

export function callTicket(id: string, pin: string) {
  return staffPost<Ticket>(`/api/tickets/${id}/call`, pin);
}

export function startVisit(id: string, pin: string) {
  return staffPost<Ticket>(`/api/tickets/${id}/start`, pin);
}

export function completeVisit(id: string, pin: string) {
  return staffPost<Ticket>(`/api/tickets/${id}/complete`, pin);
}

export function markNoShow(id: string, pin: string) {
  return staffPost<Ticket>(`/api/tickets/${id}/no-show`, pin);
}

export function pauseQueue(pin: string, reason: string) {
  return staffPost<QueueSnapshot>("/api/queue/pause", pin, { reason });
}

export function resumeQueue(pin: string) {
  return staffPost<QueueSnapshot>("/api/queue/resume", pin);
}

export function deskChat(message: string, ticketId?: string) {
  return fetch("/api/desk/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, ticketId: ticketId ?? null }),
  }).then((r) => parse<DeskReply>(r));
}
