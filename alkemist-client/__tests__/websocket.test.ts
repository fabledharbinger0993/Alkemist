/**
 * Unit tests for WebSocketManager (lib/websocket.ts).
 *
 * A minimal WebSocket mock is provided via jest's manual mock approach so
 * that the tests run in jsdom without a real WebSocket server.
 */

import { WebSocketManager } from "../lib/websocket";

// ─── WebSocket mock ───────────────────────────────────────────────────────────

class MockWebSocket {
  static readonly OPEN = 1;
  static readonly CLOSED = 3;

  readyState = MockWebSocket.OPEN;
  url: string;
  onopen: (() => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;
  onmessage: ((event: { data: string }) => void) | null = null;

  sentMessages: string[] = [];

  constructor(url: string) {
    this.url = url;
  }

  send(data: string): void {
    this.sentMessages.push(data);
  }

  close(): void {
    this.readyState = MockWebSocket.CLOSED;
    this.onclose?.();
  }

  // Helpers for tests
  simulateOpen(): void {
    this.onopen?.();
  }

  simulateMessage(data: unknown): void {
    this.onmessage?.({ data: JSON.stringify(data) });
  }

  simulateError(): void {
    this.onerror?.();
  }
}

let mockWs: MockWebSocket;

beforeEach(() => {
  // Replace the global WebSocket constructor with our mock
  (global as unknown as { WebSocket: unknown }).WebSocket = jest.fn((url: string) => {
    mockWs = new MockWebSocket(url);
    return mockWs;
  });
  (global as unknown as { WebSocket: { OPEN: number } }).WebSocket.OPEN = 1;
  jest.useFakeTimers();
});

afterEach(() => {
  jest.useRealTimers();
  jest.restoreAllMocks();
});

// ─── connect ─────────────────────────────────────────────────────────────────

describe("WebSocketManager.connect", () => {
  it("creates a WebSocket connection to the provided URL", () => {
    const manager = new WebSocketManager("ws://localhost:8000/ws/test");
    manager.connect();

    expect(mockWs.url).toBe("ws://localhost:8000/ws/test");
  });

  it("does not create a second socket if already open", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    manager.connect();
    const constructorCalls = (global.WebSocket as unknown as jest.Mock).mock.calls.length;
    manager.connect(); // should be a no-op

    expect((global.WebSocket as unknown as jest.Mock).mock.calls.length).toBe(constructorCalls);
  });
});

// ─── status handler ───────────────────────────────────────────────────────────

describe("WebSocketManager status callbacks", () => {
  it("calls onStatus('connected') when socket opens", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const statusFn = jest.fn();
    manager.onStatus(statusFn);
    manager.connect();

    mockWs.simulateOpen();

    expect(statusFn).toHaveBeenCalledWith("connected");
  });

  it("calls onStatus('disconnected') when socket closes", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const statusFn = jest.fn();
    manager.onStatus(statusFn);
    manager.connect();
    // Stop automatic reconnect for this test
    manager.disconnect();

    expect(statusFn).toHaveBeenCalledWith("disconnected");
  });

  it("calls onStatus('error') when socket errors", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const statusFn = jest.fn();
    manager.onStatus(statusFn);
    manager.connect();

    mockWs.simulateError();

    expect(statusFn).toHaveBeenCalledWith("error");
  });
});

// ─── on / message dispatch ───────────────────────────────────────────────────

describe("WebSocketManager.on", () => {
  it("calls registered handler for matching message type", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const handler = jest.fn();
    manager.on("output", handler);
    manager.connect();

    mockWs.simulateMessage({ type: "output", data: "hello\r\n" });

    expect(handler).toHaveBeenCalledWith({ type: "output", data: "hello\r\n" });
  });

  it("does not call handler for non-matching type", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const handler = jest.fn();
    manager.on("output", handler);
    manager.connect();

    mockWs.simulateMessage({ type: "status", data: "ready" });

    expect(handler).not.toHaveBeenCalled();
  });

  it("wildcard handler receives all message types", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const handler = jest.fn();
    manager.on("*", handler);
    manager.connect();

    mockWs.simulateMessage({ type: "output", data: "a" });
    mockWs.simulateMessage({ type: "status", data: "b" });

    expect(handler).toHaveBeenCalledTimes(2);
  });

  it("unsubscribe function removes the handler", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    const handler = jest.fn();
    const unsubscribe = manager.on("output", handler);
    manager.connect();

    unsubscribe();
    mockWs.simulateMessage({ type: "output", data: "after unsub" });

    expect(handler).not.toHaveBeenCalled();
  });
});

// ─── send ─────────────────────────────────────────────────────────────────────

describe("WebSocketManager.send", () => {
  it("serialises the message to JSON and sends it", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    manager.connect();

    manager.send({ type: "input", data: "ls\n" });

    expect(mockWs.sentMessages).toHaveLength(1);
    expect(JSON.parse(mockWs.sentMessages[0])).toEqual({ type: "input", data: "ls\n" });
  });

  it("does not throw when socket is not open", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    // Do not call connect() — no socket exists
    expect(() => manager.send({ type: "input", data: "x" })).not.toThrow();
  });
});

// ─── disconnect ───────────────────────────────────────────────────────────────

describe("WebSocketManager.disconnect", () => {
  it("closes the socket and prevents reconnect", () => {
    const manager = new WebSocketManager("ws://localhost:8000");
    manager.connect();
    manager.disconnect();

    expect(mockWs.readyState).toBe(MockWebSocket.CLOSED);
    // Fast-forward timers — no reconnect should happen
    jest.runAllTimers();
    expect((global.WebSocket as unknown as jest.Mock).mock.calls.length).toBe(1);
  });
});
