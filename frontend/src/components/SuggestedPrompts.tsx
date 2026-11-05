"use client";

import React from "react";
import { ArrowUpRight, HelpCircle } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface SuggestedPromptsProps {
  currentLanguage: LanguageCode;
  onSelectPrompt: (promptText: string) => void;
}

export function SuggestedPrompts({
  currentLanguage,
  onSelectPrompt,
}: SuggestedPromptsProps) {
  const t = translations[currentLanguage];

  return (
    <div className="w-full max-w-4xl mx-auto px-4 mt-8 mb-6">
      <div className="flex items-center gap-2 mb-3">
        <HelpCircle className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
        <h3 className="text-xs font-semibold uppercase tracking-wider" style={{ color: "var(--text-muted)" }}>
          {t.recentChats ? "Suggested Topics" : "Suggested Topics"}
        </h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {t.suggestedPrompts.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectPrompt(item.prompt)}
            className="group flex flex-col justify-between text-start p-4 rounded-xl border transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-color)",
            }}
          >
            <div className="flex items-start justify-between gap-2 mb-2 w-full">
              <span
                className="text-sm font-semibold group-hover:text-emerald-700 dark:group-hover:text-emerald-400 transition-colors"
                style={{ color: "var(--text-main)" }}
              >
                {item.title}
              </span>
              <ArrowUpRight className="w-4 h-4 shrink-0 opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all text-emerald-600" />
            </div>
            <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--text-muted)" }}>
              {item.description}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}

