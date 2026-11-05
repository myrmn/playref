import React from "react";
import { ShieldAlert } from "lucide-react";

interface DisclaimerFooterProps {
  text: string;
}

export function DisclaimerFooter({ text }: DisclaimerFooterProps) {
  return (
    <footer
      className="w-full py-3 px-4 text-center border-t text-xs transition-colors"
      style={{
        borderColor: "var(--border-color)",
        color: "var(--text-muted)",
        backgroundColor: "var(--bg-app)",
      }}
    >
      <div className="max-w-4xl mx-auto flex items-center justify-center gap-1.5 flex-wrap">
        <ShieldAlert className="w-3.5 h-3.5 opacity-70 shrink-0" />
        <span>{text}</span>
      </div>
    </footer>
  );
}

