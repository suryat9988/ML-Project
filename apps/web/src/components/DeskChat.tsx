import { useState, type FormEvent } from "react";
import { deskChat } from "../api";
import type { DeskReply } from "../types";

type Msg = { role: "you" | "desk"; text: string; emergency?: boolean };

export function DeskChat({ ticketId }: { ticketId?: string }) {
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "desk",
      text: "Front desk here. Ask about hours, wait time, parking, or what to bring.",
    },
  ]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const text = input.trim();
    if (!text) return;
    setInput("");
    setError("");
    setMessages((m) => [...m, { role: "you", text }]);
    setBusy(true);
    try {
      const res: DeskReply = await deskChat(text, ticketId);
      setMessages((m) => [
        ...m,
        { role: "desk", text: res.reply, emergency: res.emergency },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="chat" aria-labelledby="chat-heading">
      <h2 id="chat-heading">Ask the front desk</h2>
      <ul className="chat-log">
        {messages.map((m, i) => (
          <li key={i} className={`bubble bubble-${m.role} ${m.emergency ? "bubble-emergency" : ""}`}>
            <span className="bubble-who">{m.role === "you" ? "You" : "Desk"}</span>
            {m.text}
          </li>
        ))}
      </ul>
      {error ? (
        <p className="form-error" role="alert">
          {error}
        </p>
      ) : null}
      <form className="chat-form" onSubmit={onSubmit}>
        <label className="sr-only" htmlFor="desk-msg">
          Message
        </label>
        <input
          id="desk-msg"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. How long is the wait?"
          autoComplete="off"
        />
        <button type="submit" className="primary" disabled={busy}>
          {busy ? "Sending…" : "Send"}
        </button>
      </form>
      <p className="hint">Not medical advice. For emergencies call 911.</p>
    </section>
  );
}
