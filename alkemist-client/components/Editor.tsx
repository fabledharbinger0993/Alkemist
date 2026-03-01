"use client";

import { useCallback, useRef } from "react";
import MonacoEditor, { type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";

// ─── Types ────────────────────────────────────────────────────────────────────

interface EditorProps {
  path: string;
  content: string;
  language: string;
  onChange: (value: string) => void;
  onSave: (value: string) => void;
}

// ─── Monaco theme ─────────────────────────────────────────────────────────────

const ALKEMIST_THEME: editor.IStandaloneThemeData = {
  base: "vs-dark",
  inherit: true,
  rules: [
    { token: "comment", foreground: "4a4a6a", fontStyle: "italic" },
    { token: "keyword", foreground: "c084fc" },
    { token: "string", foreground: "86efac" },
    { token: "number", foreground: "fbbf24" },
    { token: "type", foreground: "67e8f9" },
    { token: "function", foreground: "a78bfa" },
  ],
  colors: {
    "editor.background": "#111118",
    "editor.foreground": "#e2e8f0",
    "editorLineNumber.foreground": "#2e2e3e",
    "editorLineNumber.activeForeground": "#7c3aed",
    "editor.selectionBackground": "#2e2e5e",
    "editor.lineHighlightBackground": "#1a1a24",
    "editorCursor.foreground": "#8b5cf6",
    "editorIndentGuide.background": "#1a1a24",
    "editorIndentGuide.activeBackground": "#2e2e3e",
  },
};

// ─── Component ────────────────────────────────────────────────────────────────

export function Editor({ path, content, language, onChange, onSave }: EditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleMount: OnMount = useCallback(
    (editorInstance, monaco) => {
      editorRef.current = editorInstance;

      // Register custom theme
      monaco.editor.defineTheme("alkemist-dark", ALKEMIST_THEME);
      monaco.editor.setTheme("alkemist-dark");

      // Ctrl/Cmd+S → save
      editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS,
        () => {
          const value = editorInstance.getValue();
          onSave(value);
        }
      );
    },
    [onSave]
  );

  const handleChange = useCallback(
    (value: string | undefined) => {
      onChange(value ?? "");
    },
    [onChange]
  );

  return (
    <MonacoEditor
      key={path}
      height="100%"
      language={language}
      value={content}
      theme="alkemist-dark"
      onChange={handleChange}
      onMount={handleMount}
      options={{
        fontSize: 13,
        fontFamily: "JetBrains Mono, Fira Code, Cascadia Code, monospace",
        fontLigatures: true,
        lineNumbers: "on",
        minimap: { enabled: false },
        scrollBeyondLastLine: false,
        automaticLayout: true,
        tabSize: 2,
        wordWrap: "on",
        bracketPairColorization: { enabled: true },
        smoothScrolling: true,
        cursorBlinking: "smooth",
        renderWhitespace: "selection",
        padding: { top: 12, bottom: 12 },
      }}
    />
  );
}
