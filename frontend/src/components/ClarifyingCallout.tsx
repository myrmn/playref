"use client";

import React, { useState } from "react";
import { HelpCircle, Send } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface ClarifyingCalloutProps {
  question: string;
  language: LanguageCode;
  onAnswer: (answerText: string) => void;
  disabled?: boolean;
}

export function ClarifyingCallout({
  question,
  language,
  onAnswer,
  disabled = false,
}: ClarifyingCalloutProps) {
  const t = translations[language];
  const [customInput, setCustomInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (customInput.trim() && !disabled) {
      onAnswer(customInput.trim());
      setCustomInput("");
    }
  };

  // Generate sensible quick-response suggestions if it's a binary/temporal question
  const isYesNo = /yes or no|oui ou non|نعم أم لا/i.test(question);
  const isBeforeAfter = /before or after|avant ou après|قبل أم بعد/i.test(question);
  const isInsideOutside = /inside or outside|dans ou hors|داخل أم خارج/i.test(question);

  let quickOptions: string[] = [];
  if (isYesNo) {
    quickOptions = language === "ar" ? ["نعم", "لا", "غير متأكد"] : language === "fr" ? ["Oui", "Non", "Pas sûr"] : ["Yes", "No", "Not sure"];
  } else if (isBeforeAfter) {
    quickOptions = language === "ar" ? ["قبل", "بعد", "غير واضح"] : language === "fr" ? ["Avant", "Après", "Pas certain"] : ["Before", "After", "Not sure"];
  } else if (isInsideOutside) {
    quickOptions = language === "ar" ? ["داخل منطقة الجزاء", "خارج منطقة الجزاء", "على الخط تماماً"] : language === "fr" ? ["Dans la surface", "Hors de la surface", "Sur la ligne"] : ["Inside penalty area", "Outside penalty area", "On the line"];
  }

  return (
    <div
      className="mt-4 p-4 rounded-xl border transition-colors shadow-xs"
      style={{
        backgroundColor: "var(--referee-yellow-bg)",
        borderColor: "var(--referee-yellow-border)",
      }}
    >
      <div className="flex items-start gap-2.5 mb-2.5">
        <div
          className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5"
          style={{ backgroundColor: "var(--referee-yellow)", color: "#16211B" }}
        >
          <HelpCircle className="w-4 h-4 stroke-[2.2]" />
        </div>
        <div>
          <span className="text-xs font-bold tracking-wide uppercase" style={{ color: "#875C00" }}>
            {t.answerCard.clarifyingDetail}
          </span>
          <p className="text-sm font-semibold mt-0.5" style={{ color: "var(--text-main)" }}>
            {question}
          </p>
        </div>
      </div>

      {/* Quick Option Buttons */}
      {quickOptions.length > 0 && (
        <div className="flex flex-wrap gap-2 mt-3 mb-2">
          {quickOptions.map((opt, idx) => (
            <button
              key={idx}
              type="button"
              disabled={disabled}
              onClick={() => onAnswer(opt)}
              className="px-3 py-1 text-xs font-semibold rounded-lg border bg-white dark:bg-[#16201B] hover:border-emerald-600 transition-all shadow-xs cursor-pointer disabled:opacity-50"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
              }}
            >
              {opt}
            </button>
          ))}
        </div>
      )}

      {/* Custom input line */}
      <form onSubmit={handleSubmit} className="mt-3 flex items-center gap-2">
        <input
          type="text"
          value={customInput}
          disabled={disabled}
          onChange={(e) => setCustomInput(e.target.value)}
          placeholder={t.answerCard.orCustomAnswer}
          className="flex-1 px-3 py-1.5 text-xs rounded-lg border bg-white dark:bg-[#16201B] focus:outline-none transition-all"
          style={{
            borderColor: "var(--border-color)",
            color: "var(--text-main)",
          }}
        />
        <button
          type="submit"
          disabled={!customInput.trim() || disabled}
          className="px-3 py-1.5 text-xs font-semibold rounded-lg flex items-center gap-1 text-white transition-opacity disabled:opacity-40"
          style={{ backgroundColor: "var(--pitch-green)" }}
        >
          <span>{t.answerCard.submitClarification}</span>
          <Send className="w-3 h-3" />
        </button>
      </form>
    </div>
  );
}

