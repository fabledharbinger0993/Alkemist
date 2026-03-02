import { type ReactNode } from "react";

interface HoverHintProps {
  children: ReactNode;
  hint: string;
  side?: "right" | "left";
}

export function HoverHint({ children, hint, side = "right" }: HoverHintProps) {
  const sideClasses =
    side === "left"
      ? "right-full mr-2"
      : "left-full ml-2";

  return (
    <div className="relative group">
      {children}
      <div
        className={`pointer-events-none absolute top-1/2 z-50 -translate-y-1/2 rounded border border-surface-600 bg-surface-800/85 px-2 py-1 text-[11px] text-gray-200 opacity-0 shadow-md backdrop-blur-sm transition-opacity duration-150 group-hover:opacity-100 whitespace-nowrap ${sideClasses}`}
      >
        {hint}
      </div>
    </div>
  );
}
