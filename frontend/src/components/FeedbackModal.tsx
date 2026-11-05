"use client";

import React, { useState } from "react";
import { AlertTriangle, CheckCircle2, X } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface FeedbackModalProps {
  isOpen: boolean;
  messageId: string;
  language: LanguageCode;
  onClose: () => void;
  onSubmit: (data: { messageId: string; rating: number; reason: string; comment?: string }) => Promise<void>;
}

export function FeedbackModal({
  isOpen,
  messageId,
  language,
  onClose,
  onSubmit,
}: FeedbackModalProps) {
  const t = translations[language];
  const [selectedReason, setSelectedReason] = useState<string>("wrong_law_cited");
  const [comment, setComment] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onSubmit({
        messageId,
        rating: -1,
        reason: selectedReason,
        comment: comment.trim() || undefined,
      });
      setIsSuccess(true);
      setTimeout(() => {
        setIsSuccess(false);
        onClose();
      }, 1400);
    } catch {
      setIsSubmitting(false);
    }
  };

  const options = [
    { id: "wrong_law_cited", label: t.feedbackModal.optionWrongLaw },
    { id: "missing_relevant_law", label: t.feedbackModal.optionMissingLaw },
    { id: "unclear_or_contradictory", label: t.feedbackModal.optionUnclear },
    { id: "other", label: t.feedbackModal.optionOther },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        className="relative w-full max-w-md rounded-2xl border p-6 shadow-xl transition-all"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-color)",
          color: "var(--text-main)",
        }}
      >
        <button
          onClick={onClose}
          className="absolute top-4 end-4 p-1 rounded-lg opacity-60 hover:opacity-100 transition-opacity"
        >
          <X className="w-5 h-5" />
        </button>

        {isSuccess ? (
          <div className="py-8 flex flex-col items-center justify-center text-center gap-3">
            <CheckCircle2 className="w-12 h-12 text-emerald-600 animate-in zoom-in duration-200" />
            <h4 className="font-bold text-lg">{t.answerCard.feedbackThanks}</h4>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                style={{ backgroundColor: "var(--card-red-bg)", color: "var(--card-red)" }}
              >
                <AlertTriangle className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-bold text-base">{t.feedbackModal.title}</h3>
                <p className="text-xs opacity-70">{t.feedbackModal.subtitle}</p>
              </div>
            </div>

            <div className="flex flex-col gap-2.5 mt-2">
              {options.map((opt) => (
                <label
                  key={opt.id}
                  className="flex items-center gap-3 p-3 rounded-xl border cursor-pointer transition-colors hover:bg-black/5 dark:hover:bg-white/5"
                  style={{
                    borderColor:
                      selectedReason === opt.id ? "var(--pitch-green)" : "var(--border-color)",
                    backgroundColor:
                      selectedReason === opt.id ? "var(--bg-tint)" : "transparent",
                  }}
                >
                  <input
                    type="radio"
                    name="reason"
                    value={opt.id}
                    checked={selectedReason === opt.id}
                    onChange={(e) => setSelectedReason(e.target.value)}
                    className="accent-emerald-700 w-4 h-4 cursor-pointer"
                  />
                  <span className="text-xs font-semibold">{opt.label}</span>
                </label>
              ))}
            </div>

            <div className="flex flex-col gap-1.5 mt-1">
              <textarea
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder={t.feedbackModal.commentPlaceholder}
                className="w-full p-3 text-xs rounded-xl border bg-transparent focus:outline-none resize-none transition-colors"
                style={{ borderColor: "var(--border-color)", color: "var(--text-main)" }}
              />
            </div>

            <div className="flex items-center justify-end gap-2.5 mt-2">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs font-semibold rounded-xl border hover:opacity-80 transition-opacity"
                style={{ borderColor: "var(--border-color)" }}
              >
                {t.feedbackModal.cancel}
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 text-xs font-semibold rounded-xl text-white shadow-xs hover:opacity-90 transition-opacity disabled:opacity-50"
                style={{ backgroundColor: "var(--pitch-green)" }}
              >
                {isSubmitting ? "..." : t.feedbackModal.submit}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

