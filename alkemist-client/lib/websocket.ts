// WebSocket URL — direct connection to FastAPI (bypasses Next.js proxy for WS)
export const WS_URL =
  process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8000";

// ─── Types ────────────────────────────────────────────────────────────────────

type MessageHandler = (data: unknown) => void;
type StatusHandler = (status: "connected" | "disconnected" | "error") => void;

interface WsMessage {
  type: string;
  [key: string]: unknown;
}

// ─── WebSocket manager ────────────────────────────────────────────────────────

export class WebSocketManager {
  private ws: WebSocket | null = null;
  private readonly url: string;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly handlers = new Map<string, Set<MessageHandler>>();
  private statusHandler: StatusHandler | null = null;
  private shouldReconnect = true;

  constructor(url: string) {
    this.url = url;
  }

  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) return;

    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.statusHandler?.("connected");
    };

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data as string) as WsMessage;
        const handlers = this.handlers.get(msg.type);
        handlers?.forEach((h) => h(msg));
        this.handlers.get("*")?.forEach((h) => h(msg));
      } catch {
        // raw data — broadcast to wildcard handlers
        this.handlers.get("*")?.forEach((h) => h(event.data));
      }
    };

    this.ws.onclose = () => {
      this.statusHandler?.("disconnected");
      if (this.shouldReconnect) {
        this.reconnectTimer = setTimeout(() => this.connect(), 3000);
      }
    };

    this.ws.onerror = () => {
      this.statusHandler?.("error");
    };
  }

  send(message: WsMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  on(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    // Return unsubscribe fn
    return () => this.handlers.get(type)?.delete(handler);
  }

  onStatus(handler: StatusHandler): void {
    this.statusHandler = handler;
  }

  disconnect(): void {
    this.shouldReconnect = false;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
  }
}
