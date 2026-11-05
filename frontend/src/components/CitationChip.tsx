"use client";

import React from "react";
import { BookOpen, ExternalLink } from "lucide-react";

interface CitationChipProps {
  citation: string;
  chunkId: string;
  quoteOrSummary?: string;
  onClick: (chunkId: string) => void;
  className?: string;
}

export function CitationChip({
  citation,
  chunkId,
  quoteOrSummary,
  onClick,
  className = "",
}: CitationChipProps) {
  return (
    <button
      onClick={() => onClick(chunkId)}
      title={quoteOrSummary || `Inspect ${citation} in IFAB Laws of the Game`}
      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all duration-150 hover:scale-[1.02] active:scale-[0.98] cursor-pointer shadow-xs ${className}`}
      style={{
        backgroundColor: "var(--bg-tint)",
        borderColor: "rgba(15, 123, 75, 0.3)",
        color: "var(--pitch-green)",
      }}
    >
      <BookOpen className="w-3.5 h-3.5 shrink-0 stroke-[1.8]" />
      <span className="font-semibold">{citation}</span>
      <ExternalLink className="w-3 h-3 opacity-60 ml-0.5 shrink-0" />
    </button>
  );
}

