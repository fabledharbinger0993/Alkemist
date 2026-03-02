"use client";

import { useEffect, useRef } from "react";
import { WS_URL } from "@/lib/websocket";
import "@xterm/xterm/css/xterm.css";

// ─── Types ────────────────────────────────────────────────────────────────────

interface TerminalProps {
  projectId: string;
}

// ─── Component ────────────────────────────────────────────────────────────────

export function Terminal({ projectId }: TerminalProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<any>(null);
  const fitAddonRef = useRef<any>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let resizeObserver: ResizeObserver | null = null;
    let term: any = null;

    const initializeTerminal = async () => {
      const [{ Terminal: XTerm }, { FitAddon }, { WebLinksAddon }] = await Promise.all([
        import("@xterm/xterm"),
        import("@xterm/addon-fit"),
        import("@xterm/addon-web-links"),
      ]);

      if (!containerRef.current) return;

      // ── Create xterm instance ─────────────────────────────────────────────
      const termInstance = new XTerm({
        theme: {
          background: "#0a0a0f",
          foreground: "#e2e8f0",
          cursor: "#8b5cf6",
          selectionBackground: "#2e2e5e",
          black: "#1a1a24",
          brightBlack: "#2e2e3e",
          red: "#f87171",
          green: "#86efac",
          yellow: "#fbbf24",
          blue: "#93c5fd",
          magenta: "#c084fc",
          cyan: "#67e8f9",
          white: "#e2e8f0",
          brightWhite: "#f8fafc",
        },
        fontSize: 12,
        fontFamily: "JetBrains Mono, Fira Code, monospace",
        cursorBlink: true,
        convertEol: true,
        scrollback: 2000,
      });
      term = termInstance;

      const fitAddon = new FitAddon();
      const webLinksAddon = new WebLinksAddon();
      termInstance.loadAddon(fitAddon);
      termInstance.loadAddon(webLinksAddon);
      termInstance.open(containerRef.current);
      fitAddon.fit();

      xtermRef.current = termInstance;
      fitAddonRef.current = fitAddon;

      // ── WebSocket connection ──────────────────────────────────────────────
      const ws = new WebSocket(`${WS_URL}/ws/terminal/${projectId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        termInstance.writeln("\x1b[32m● Connected to Alkemist terminal\x1b[0m");
        // Send initial terminal size
        ws.send(
          JSON.stringify({
            type: "resize",
            cols: termInstance.cols,
            rows: termInstance.rows,
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data as string) as {
            type: string;
            data: string;
          };
          if (msg.type === "output") {
            termInstance.write(msg.data);
          }
        } catch {
          termInstance.write(event.data as string);
        }
      };

      ws.onclose = () => {
        termInstance.writeln("\r\n\x1b[33m● Connection closed\x1b[0m");
      };

      ws.onerror = () => {
        termInstance.writeln(
          "\r\n\x1b[31m● WebSocket error — is the server running?\x1b[0m"
        );
      };

      // Forward keyboard input to WebSocket
      termInstance.onData((data: string) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: "input", data }));
        }
      });

      // Forward resize events
      resizeObserver = new ResizeObserver(() => {
        fitAddon.fit();
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(
            JSON.stringify({
              type: "resize",
              cols: termInstance.cols,
              rows: termInstance.rows,
            })
          );
        }
      });
      if (containerRef.current) {
        resizeObserver.observe(containerRef.current);
      }
    };

    void initializeTerminal();

    return () => {
      resizeObserver?.disconnect();
      wsRef.current?.close();
      term?.dispose();
    };
  }, [projectId]);

  return (
    <div className="h-full bg-surface-950 flex flex-col">
      <div className="flex items-center px-3 py-1 bg-surface-900 border-b border-surface-700 text-xs text-gray-500">
        <span className="text-green-400 mr-2">●</span>
        Terminal
      </div>
      <div ref={containerRef} className="flex-1 overflow-hidden" />
    </div>
  );
}
