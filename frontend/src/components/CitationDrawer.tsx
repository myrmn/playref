"use client";

import React, { useEffect, useState } from "react";
import { BookOpen, Check, Copy, ExternalLink, Loader2, X } from "lucide-react";
import { ChunkMetadata, LanguageCode } from "@/lib/types";
import { getChunk } from "@/lib/api";
import { translations } from "@/lib/translations";

interface CitationDrawerProps {
  chunkId: string | null;
  isOpen: boolean;
  language: LanguageCode;
  onClose: () => void;
  onOpenInLawBrowser: (lawNumber: number) => void;
}

export function CitationDrawer({
  chunkId,
  isOpen,
  language,
  onClose,
  onOpenInLawBrowser,
}: CitationDrawerProps) {
  const t = translations[language];
  const [chunk, setChunk] = useState<ChunkMetadata | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!isOpen || !chunkId) return;

    let isMounted = true;
    Promise.resolve().then(() => {
      if (isMounted) {
        setLoading(true);
        setError(null);
      }
    });

    getChunk(chunkId)
      .then((data) => {
        if (isMounted) {
          setChunk(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err instanceof Error ? err.message : "Failed to load citation text");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, [chunkId, isOpen]);

  if (!isOpen) return null;

  const handleCopy = async () => {
    if (!chunk) return;
    const textToCopy = `[Law ${chunk.law_number} - ${chunk.law_title}]\nSection: ${chunk.section_path}\nPage: ${chunk.page} (Edition: ${chunk.edition})\n\n"${chunk.clean_text}"`;
    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // ignore
    }
  };

  const isRtl = language === "ar";

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="fixed inset-0 bg-black/40 backdrop-blur-xs transition-opacity animate-in fade-in duration-200"
      />

      <div
        className={`fixed inset-y-0 ${
          isRtl ? "start-0" : "end-0"
        } max-w-full flex sm:w-[480px] w-full z-50`}
      >
        <div
          className="w-full h-full flex flex-col shadow-2xl border-s border-e transition-all animate-in duration-300 slide-in-from-right"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-color)",
            color: "var(--text-main)",
          }}
        >
          {/* Header */}
          <div
            className="p-5 border-b flex items-start justify-between gap-3"
            style={{ borderColor: "var(--border-color)" }}
          >
            <div className="flex items-center gap-3">
              {chunk ? (
                <div
                  className="px-2.5 py-1 rounded-lg text-xs font-bold text-white uppercase tracking-wider shrink-0"
                  style={{ backgroundColor: "var(--pitch-green)" }}
                >
                  {t.citationDrawer.law} {chunk.law_number}
                </div>
              ) : (
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  style={{ backgroundColor: "var(--bg-tint)", color: "var(--pitch-green)" }}
                >
                  <BookOpen className="w-4 h-4" />
                </div>
              )}

              <div>
                <h3 className="font-bold text-base leading-tight">
                  {chunk ? chunk.law_title : t.citationDrawer.title}
                </h3>
                {chunk && (
                  <p className="text-xs mt-0.5 opacity-70 leading-snug">
                    {chunk.section_path}
                  </p>
                )}
              </div>
            </div>

            <button
              onClick={onClose}
              aria-label={t.citationDrawer.close}
              className="p-1.5 rounded-lg opacity-60 hover:opacity-100 transition-opacity"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Body Content */}
          <div className="flex-1 overflow-y-auto p-5 sm:p-6 space-y-5">
            {loading ? (
              <div className="h-64 flex flex-col items-center justify-center gap-2 opacity-60">
                <Loader2 className="w-7 h-7 animate-spin text-emerald-600" />
                <span className="text-xs">{t.lawBrowserView.loadingLaw}</span>
              </div>
            ) : error ? (
              <div
                className="p-4 rounded-xl border text-xs"
                style={{
                  backgroundColor: "var(--card-red-bg)",
                  borderColor: "var(--card-red-border)",
                  color: "var(--card-red)",
                }}
              >
                {error}
              </div>
            ) : chunk ? (
              <>
                {/* Official IFAB Passage */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[11px] font-bold uppercase tracking-wider opacity-60">
                      {t.citationDrawer.officialText}
                    </span>
                    <span className="text-[11px] font-mono opacity-50">
                      {chunk.chunk_id}
                    </span>
                  </div>

                  <div
                    className="p-4 rounded-xl border leading-relaxed text-[15px] sm:text-[16px] whitespace-pre-wrap font-serif sm:font-sans selection:bg-emerald-200"
                    style={{
                      backgroundColor: "var(--bg-app)",
                      borderColor: "var(--border-color)",
                      color: "var(--text-main)",
                    }}
                  >
                    {chunk.clean_text}
                  </div>
                </div>

                {/* Metadata Row */}
                <div
                  className="p-3 rounded-xl border text-xs flex flex-wrap items-center justify-between gap-2 opacity-80"
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    borderColor: "var(--border-color)",
                  }}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{t.citationDrawer.page}:</span>
                    <span>{chunk.page}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{t.citationDrawer.edition}:</span>
                    <span>{chunk.edition}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">{t.citationDrawer.source}:</span>
                    <span>{chunk.source}</span>
                  </div>
                </div>
              </>
            ) : null}
          </div>

          {/* Footer Action Buttons */}
          {chunk && (
            <div
              className="p-4 border-t flex items-center justify-between gap-3"
              style={{ borderColor: "var(--border-color)", backgroundColor: "var(--bg-app)" }}
            >
              <button
                onClick={() => {
                  onOpenInLawBrowser(chunk.law_number);
                  onClose();
                }}
                className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl border hover:border-emerald-600 transition-colors"
                style={{
                  borderColor: "var(--border-color)",
                  backgroundColor: "var(--bg-surface)",
                  color: "var(--text-main)",
                }}
              >
                <ExternalLink className="w-3.5 h-3.5" />
                <span>{t.citationDrawer.openInLawBrowser}</span>
              </button>

              <button
                onClick={handleCopy}
                className="flex items-center gap-1.5 px-3.5 py-2 text-xs font-semibold rounded-xl text-white shadow-xs transition-transform active:scale-95"
                style={{ backgroundColor: "var(--pitch-green)" }}
              >
                {copied ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-white" />
                    <span>{t.citationDrawer.citationCopied}</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>{t.citationDrawer.copyCitation}</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

