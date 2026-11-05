"use client";

import React from "react";
import { Square, Search, ShieldCheck, PenTool } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface StageIndicatorProps {
  stage: string;
  language: LanguageCode;
  onStop: () => void;
}

export function StageIndicator({ stage, language, onStop }: StageIndicatorProps) {
  const t = translations[language];

  // Map internal stage names to friendly labels and icons
  let label = t.stages.searching;
  let Icon = Search;

  if (stage.includes("route") || stage.includes("intent")) {
    label = t.stages.routing;
    Icon = Search;
  } else if (stage.includes("check") || stage.includes("rerank") || stage.includes("retrieve")) {
    label = t.stages.checking;
    Icon = ShieldCheck;
  } else if (stage.includes("write") || stage.includes("generate") || stage.includes("delta")) {
    label = t.stages.writing;
    Icon = PenTool;
  }

  return (
    <div
      className="w-full max-w-4xl mx-auto my-3 px-4 py-2.5 rounded-xl border flex items-center justify-between text-xs font-medium shadow-xs animate-in fade-in duration-150"
      style={{
        backgroundColor: "var(--bg-tint)",
        borderColor: "rgba(15, 123, 75, 0.3)",
        color: "var(--pitch-green)",
      }}
    >
      <div className="flex items-center gap-2.5">
        <Icon className="w-4 h-4 animate-bounce text-emerald-700 dark:text-emerald-400" />
        <span className="font-semibold">{label}</span>
        <span className="flex gap-1 ms-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-stage-pulse" />
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-stage-pulse [animation-delay:200ms]" />
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-stage-pulse [animation-delay:400ms]" />
        </span>
      </div>

      <button
        type="button"
        onClick={onStop}
        className="flex items-center gap-1 px-2.5 py-1 rounded-lg text-[11px] font-bold text-white shadow-xs transition-opacity hover:opacity-90 cursor-pointer"
        style={{ backgroundColor: "var(--card-red)" }}
      >
        <Square className="w-3 h-3 fill-current" />
        <span>{t.stop}</span>
      </button>
    </div>
  );
}

