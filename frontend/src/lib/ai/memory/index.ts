export interface AIMemoryEntry {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
}

export interface AISession {
  id: string;
  title: string;
  messages: AIMemoryEntry[];
  createdAt: number;
  updatedAt: number;
  isStarred: boolean;
  metadata?: Record<string, unknown>;
}

const STORAGE_KEY = "jobnav-ai-sessions";

function loadSessions(): AISession[] {
  if (typeof window === "undefined") return [];
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]"); } catch { return []; }
}

function saveSessions(sessions: AISession[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
}

export class AIMemory {
  private sessions: AISession[] = [];
  private currentSessionId: string | null = null;

  constructor() { this.sessions = loadSessions(); }

  createSession(title?: string): AISession {
    const session: AISession = {
      id: crypto.randomUUID(),
      title: title || "新对话",
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
      isStarred: false,
    };
    this.sessions.unshift(session);
    this.currentSessionId = session.id;
    saveSessions(this.sessions);
    return session;
  }

  getCurrentSession(): AISession | null {
    if (!this.currentSessionId) return null;
    return this.sessions.find((s) => s.id === this.currentSessionId) || null;
  }

  switchSession(id: string) { this.currentSessionId = id; }

  addMessage(role: AIMemoryEntry["role"], content: string) {
    const session = this.getCurrentSession() || this.createSession();
    const entry: AIMemoryEntry = { role, content, timestamp: Date.now() };
    session.messages.push(entry);
    session.updatedAt = Date.now();
    if (session.messages.length === 1 && role === "user") {
      session.title = content.slice(0, 50) + (content.length > 50 ? "..." : "");
    }
    saveSessions(this.sessions);
  }

  getMessages(): AIMemoryEntry[] {
    return this.getCurrentSession()?.messages || [];
  }

  getAllSessions(): AISession[] { return this.sessions; }

  deleteSession(id: string) {
    this.sessions = this.sessions.filter((s) => s.id !== id);
    if (this.currentSessionId === id) this.currentSessionId = this.sessions[0]?.id || null;
    saveSessions(this.sessions);
  }

  toggleStar(id: string) {
    const session = this.sessions.find((s) => s.id === id);
    if (session) { session.isStarred = !session.isStarred; saveSessions(this.sessions); }
  }

  renameSession(id: string, title: string) {
    const session = this.sessions.find((s) => s.id === id);
    if (session) { session.title = title; saveSessions(this.sessions); }
  }

  clear() { this.sessions = []; this.currentSessionId = null; saveSessions(this.sessions); }
}

let _instance: AIMemory | null = null;
export function getAIMemory(): AIMemory {
  if (!_instance) _instance = new AIMemory();
  return _instance;
}
