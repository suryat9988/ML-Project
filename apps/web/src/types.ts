export type VisitReason =
  | "cold_flu"
  | "minor_injury"
  | "physical"
  | "vaccination"
  | "prescription"
  | "other";

export type TicketStatus =
  | "waiting"
  | "called"
  | "in_visit"
  | "completed"
  | "no_show";

export type Provider = {
  id: string;
  name: string;
  specialty: string;
  room: string;
};

export type ClinicHours = {
  weekday: string;
  open: string;
  close: string;
};

export type Clinic = {
  name: string;
  address: string;
  phone: string;
  parking: string;
  insuranceNotes: string;
  whatToBring: string[];
  hours: ClinicHours[];
  providers: Provider[];
  minutesPerVisit: number;
  staffPinHint: string;
};

export type Ticket = {
  id: string;
  token: string;
  patientName: string;
  phone: string;
  reason: VisitReason;
  reasonLabel: string;
  providerId: string;
  providerName: string;
  status: TicketStatus;
  position: number;
  etaMinutes: number;
  createdAt: string;
  updatedAt: string;
  calledAt: string | null;
  notes: string;
};

export type QueueSnapshot = {
  paused: boolean;
  pauseReason: string;
  waitingCount: number;
  inVisitCount: number;
  completedToday: number;
  tickets: Ticket[];
};

export type DeskReply = {
  reply: string;
  disclaimer: string;
  emergency: boolean;
};

export type CheckInInput = {
  patientName: string;
  phone: string;
  reason: VisitReason;
  providerId: string;
  notes?: string;
};
