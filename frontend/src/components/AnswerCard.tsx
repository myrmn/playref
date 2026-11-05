"use client";

import React, { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  Scale,
  Sparkles,
  Info,
  CheckCircle2,
  Sliders,
} from "lucide-react";
import { AnswerPayload, LanguageCode } from "@/lib/types";
import { CitationChip } from "./CitationChip";
import { ClarifyingCallout } from "./ClarifyingCallout";
import { translations } from "@/lib/translations";
import { submitFeedback } from "@/lib/api";

interface AnswerCardProps {
  messageId: string;
  answer: AnswerPayload;
  language: LanguageCode;
  onOpenCitation: (chunkId: string) => void;
  onClarifyAnswer: (text: string) => void;
  onOpenFeedbackModal: (messageId: string) => void;
  isStreaming?: boolean;
}

export function AnswerCard({
  messageId,
  answer,
  language,
  onOpenCitation,
  onClarifyAnswer,
  onOpenFeedbackModal,
  isStreaming = false,
}: AnswerCardProps) {
  const t = translations[language];

  const [interpretationsOpen, setInterpretationsOpen] = useState(false);
  const [whatChangesOpen, setWhatChangesOpen] = useState(false);
  const [feedbackSent, setFeedbackSent] = useState<number | null>(null);

  const handleQuickRating = async (rating: number) => {
    if (feedbackSent !== null || !messageId) return;
    try {
      await submitFeedback({ messageId, rating });
      setFeedbackSent(rating);
    } catch {
      // ignore
    }
  };

  const hasInterpretations =
    answer.interpretations && answer.interpretations.length > 0;
  const hasWhatWouldChange =
    answer.what_would_change_the_decision &&
    answer.what_would_change_the_decision.length > 0;
  const hasAssumptions = answer.assumptions && answer.assumptions.length > 0;
  const hasApplicableLaws =
    answer.applicable_laws && answer.applicable_laws.length > 0;

  return (
    <div
      className="w-full rounded-2xl border p-5 sm:p-6 shadow-sm transition-all duration-200"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-color)",
        color: "var(--text-main)",
      }}
    >
      {/* 1. Short Answer Section */}
      <div className="flex items-start gap-3">
        <div
          className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 shadow-xs"
          style={{
            backgroundColor: "var(--bg-tint)",
            color: "var(--pitch-green)",
          }}
        >
          <Scale className="w-4 h-4 stroke-[2]" />
        </div>

        <div className="flex-1 space-y-2">
          <div className="flex items-center justify-between">
            <span
              className="text-xs font-bold uppercase tracking-wider"
              style={{ color: "var(--pitch-green)" }}
            >
              {t.answerCard.shortAnswer}
            </span>
          </div>

          <p className="text-sm sm:text-[15px] leading-relaxed whitespace-pre-line font-normal">
            {answer.short_answer}
            {isStreaming && (
              <span className="inline-block w-2 h-4 ms-1 bg-emerald-600 animate-pulse rounded-xs align-middle" />
            )}
          </p>
        </div>
      </div>

      {/* 2. Applicable Laws Chips */}
      {hasApplicableLaws && (
        <div className="mt-5 pt-4 border-t" style={{ borderColor: "var(--border-color)" }}>
          <div className="flex items-center gap-2 mb-2.5">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
            <span className="text-xs font-semibold opacity-75">
              {t.answerCard.applicableLaws}
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            {answer.applicable_laws.map((law, idx) => (
              <CitationChip
                key={`${law.chunk_id}-${idx}`}
                citation={law.citation}
                chunkId={law.chunk_id}
                quoteOrSummary={law.quote_or_summary}
                onClick={onOpenCitation}
              />
            ))}
          </div>
        </div>
      )}

      {/* 3. Possible Interpretations & Discretion (Collapsible Accordion) */}
      {hasInterpretations && (
        <div className="mt-4 border rounded-xl overflow-hidden" style={{ borderColor: "var(--border-color)" }}>
          <button
            type="button"
            onClick={() => setInterpretationsOpen(!interpretationsOpen)}
            className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold transition-colors hover:bg-black/5 dark:hover:bg-white/5"
            style={{ backgroundColor: "var(--bg-app)" }}
          >
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-emerald-700 dark:text-emerald-400" />
              <span>{t.answerCard.possibleInterpretations}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full border opacity-70">
                {answer.interpretations.length}
              </span>
            </div>
            {interpretationsOpen ? (
              <ChevronUp className="w-4 h-4 opacity-60" />
            ) : (
              <ChevronDown className="w-4 h-4 opacity-60" />
            )}
          </button>

          {interpretationsOpen && (
            <div className="p-4 space-y-2 text-xs leading-relaxed border-t" style={{ borderColor: "var(--border-color)" }}>
              <ul className="list-disc list-inside space-y-1.5 opacity-90">
                {answer.interpretations.map((item, idx) => (
                  <li key={idx} className="marker:text-emerald-600">
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 4. What Would Change the Decision (Collapsible Accordion) */}
      {hasWhatWouldChange && (
        <div className="mt-3 border rounded-xl overflow-hidden" style={{ borderColor: "var(--border-color)" }}>
          <button
            type="button"
            onClick={() => setWhatChangesOpen(!whatChangesOpen)}
            className="w-full px-4 py-3 flex items-center justify-between text-xs font-semibold transition-colors hover:bg-black/5 dark:hover:bg-white/5"
            style={{ backgroundColor: "var(--bg-app)" }}
          >
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-amber-600 dark:text-amber-400" />
              <span>{t.answerCard.whatWouldChange}</span>
              <span className="text-[10px] px-1.5 py-0.2 rounded-full border opacity-70">
                {answer.what_would_change_the_decision.length}
              </span>
            </div>
            {whatChangesOpen ? (
              <ChevronUp className="w-4 h-4 opacity-60" />
            ) : (
              <ChevronDown className="w-4 h-4 opacity-60" />
            )}
          </button>

          {whatChangesOpen && (
            <div className="p-4 space-y-2 text-xs leading-relaxed border-t" style={{ borderColor: "var(--border-color)" }}>
              <ul className="list-disc list-inside space-y-1.5 opacity-90">
                {answer.what_would_change_the_decision.map((item, idx) => (
                  <li key={idx} className="marker:text-amber-600">
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* 5. Assumptions Made (Muted List) */}
      {hasAssumptions && (
        <div className="mt-3 px-3 py-2 rounded-xl text-xs flex items-start gap-2 opacity-75" style={{ backgroundColor: "var(--bg-app)" }}>
          <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <div className="flex flex-col gap-0.5">
            <span className="font-semibold text-[11px] uppercase tracking-wider">{t.answerCard.assumptions}:</span>
            <span className="leading-snug">{answer.assumptions.join(" • ")}</span>
          </div>
        </div>
      )}

      {/* 6. Clarifying Question Callout (If bot needs more details) */}
      {answer.needs_more_info && answer.clarifying_question && (
        <ClarifyingCallout
          question={answer.clarifying_question}
          language={language}
          onAnswer={onClarifyAnswer}
          disabled={isStreaming}
        />
      )}

      {/* 7. Feedback Row */}
      {!isStreaming && (
        <div
          className="mt-5 pt-3 border-t flex items-center justify-between text-xs"
          style={{ borderColor: "var(--border-color)" }}
        >
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => handleQuickRating(1)}
              disabled={feedbackSent !== null}
              title={t.answerCard.feedbackHelpful}
              className={`p-1.5 rounded-lg border transition-all ${
                feedbackSent === 1
                  ? "bg-emerald-100 text-emerald-800 border-emerald-400 font-bold"
                  : "opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5"
              }`}
              style={{ borderColor: "var(--border-color)" }}
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => handleQuickRating(-1)}
              disabled={feedbackSent !== null}
              title={t.answerCard.feedbackNotHelpful}
              className={`p-1.5 rounded-lg border transition-all ${
                feedbackSent === -1
                  ? "bg-red-100 text-red-800 border-red-400 font-bold"
                  : "opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5"
              }`}
              style={{ borderColor: "var(--border-color)" }}
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
            {feedbackSent !== null && (
              <span className="text-[11px] text-emerald-600 font-medium ms-1 flex items-center gap-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Recorded</span>
              </span>
            )}
          </div>

          <button
            onClick={() => onOpenFeedbackModal(messageId)}
            className="flex items-center gap-1 text-[11px] font-medium opacity-65 hover:opacity-100 hover:text-red-600 transition-colors cursor-pointer"
          >
            <AlertTriangle className="w-3 h-3 text-red-500" />
            <span>{t.answerCard.wrongLawCited}</span>
          </button>
        </div>
      )}
    </div>
  );
}

