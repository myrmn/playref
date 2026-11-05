"use client";

import React, { useEffect, useState } from "react";
import { BookOpen, HelpCircle, Loader2, MessageSquare, Search } from "lucide-react";
import { LawDetail, LawSummary, LanguageCode } from "@/lib/types";
import { getLaw, listLaws } from "@/lib/api";
import { translations } from "@/lib/translations";

interface LawBrowserProps {
  language: LanguageCode;
  selectedLawNumber?: number | null;
  onSelectLawNumber?: (num: number) => void;
  onAskAboutSection: (prompt: string) => void;
}

export function LawBrowser({
  language,
  selectedLawNumber,
  onSelectLawNumber,
  onAskAboutSection,
}: LawBrowserProps) {
  const t = translations[language];

  const [laws, setLaws] = useState<LawSummary[]>([]);
  const [loadingLaws, setLoadingLaws] = useState(true);
  const [internalLawNumber, setInternalLawNumber] = useState<number>(12);
  const activeLawNumber = selectedLawNumber ?? internalLawNumber;
  const [activeLawDetail, setActiveLawDetail] = useState<LawDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Load summary list of 17 laws
  useEffect(() => {
    let isMounted = true;
    listLaws()
      .then((data) => {
        if (isMounted) {
          setLaws(data);
          setLoadingLaws(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoadingLaws(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  // Load active law details
  useEffect(() => {
    if (!activeLawNumber) return;
    let isMounted = true;
    Promise.resolve().then(() => {
      if (isMounted) setLoadingDetail(true);
    });

    getLaw(activeLawNumber)
      .then((detail) => {
        if (isMounted) {
          setActiveLawDetail(detail);
          setLoadingDetail(false);
        }
      })
      .catch(() => {
        if (isMounted) setLoadingDetail(false);
      });

    return () => {
      isMounted = false;
    };
  }, [activeLawNumber]);

  const filteredLaws = laws.filter((l) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      l.title.toLowerCase().includes(q) ||
      `law ${l.law_number}`.includes(q) ||
      `قانون ${l.law_number}`.includes(q) ||
      `loi ${l.law_number}`.includes(q)
    );
  });

  return (
    <div
      className="w-full flex-1 flex flex-col md:flex-row h-full overflow-hidden border-t"
      style={{ borderColor: "var(--border-color)", backgroundColor: "var(--bg-app)" }}
    >
      {/* Left Column: 17 Laws Sidebar */}
      <div
        className="w-full md:w-80 lg:w-96 border-b md:border-b-0 md:border-e flex flex-col h-auto md:h-full shrink-0"
        style={{
          borderColor: "var(--border-color)",
          backgroundColor: "var(--bg-surface)",
        }}
      >
        {/* Search header */}
        <div className="p-4 border-b" style={{ borderColor: "var(--border-color)" }}>
          <div className="relative">
            <Search className="w-4 h-4 absolute start-3 top-3 opacity-50" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={t.lawBrowserView.searchPlaceholder}
              className="w-full ps-9 pe-3 py-2 text-xs rounded-xl border bg-transparent focus:outline-none transition-colors"
              style={{ borderColor: "var(--border-color)", color: "var(--text-main)" }}
            />
          </div>
        </div>

        {/* Laws list */}
        <div className="flex-1 overflow-y-auto divide-y" style={{ borderColor: "var(--border-color)" }}>
          {loadingLaws ? (
            <div className="p-8 flex flex-col items-center justify-center gap-2 opacity-60">
              <Loader2 className="w-6 h-6 animate-spin text-emerald-600" />
              <span className="text-xs">{t.lawBrowserView.loadingLaw}</span>
            </div>
          ) : filteredLaws.length === 0 ? (
            <div className="p-6 text-center text-xs opacity-60">
              {t.lawBrowserView.emptySearchResults}
            </div>
          ) : (
            filteredLaws.map((law) => {
              const isActive = law.law_number === activeLawNumber;
              return (
                <button
                  key={law.law_number}
                  onClick={() => {
                    setInternalLawNumber(law.law_number);
                    onSelectLawNumber?.(law.law_number);
                  }}
                  className={`w-full p-3.5 px-4 flex items-center justify-between text-start transition-colors ${
                    isActive ? "font-semibold shadow-xs" : "opacity-80 hover:opacity-100"
                  }`}
                  style={{
                    backgroundColor: isActive ? "var(--bg-tint)" : "transparent",
                    color: isActive ? "var(--pitch-green)" : "var(--text-main)",
                  }}
                >
                  <div className="flex items-center gap-3">
                    <span
                      className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white shrink-0"
                      style={{
                        backgroundColor: isActive
                          ? "var(--pitch-green)"
                          : "rgba(15, 123, 75, 0.4)",
                      }}
                    >
                      {law.law_number}
                    </span>
                    <span className="text-xs line-clamp-1">{law.title}</span>
                  </div>
                  <span className="text-[11px] opacity-60 ms-2 shrink-0">
                    {law.chunk_count} {t.lawBrowserView.chunksCount}
                  </span>
                </button>
              );
            })
          )}
        </div>
      </div>

      {/* Right Column: Law Reader Pane */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto p-4 sm:p-6 lg:p-8">
        {loadingDetail ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-2 opacity-60 min-h-[300px]">
            <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
            <span className="text-sm">{t.lawBrowserView.loadingLaw}</span>
          </div>
        ) : activeLawDetail ? (
          <div className="max-w-4xl mx-auto w-full space-y-6">
            {/* Law Header Card */}
            <div
              className="p-6 rounded-2xl border shadow-xs"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
                <div className="flex items-center gap-2.5">
                  <span
                    className="px-3 py-1 rounded-xl text-xs font-bold text-white uppercase tracking-wider"
                    style={{ backgroundColor: "var(--pitch-green)" }}
                  >
                    Law {activeLawDetail.law_number}
                  </span>
                  <span className="text-xs opacity-60">
                    Edition: {activeLawDetail.edition}
                  </span>
                </div>

                <button
                  onClick={() =>
                    onAskAboutSection(
                      `Explain Law ${activeLawDetail.law_number} (${activeLawDetail.title}) and how it is applied in match situations.`
                    )
                  }
                  className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold rounded-xl text-white shadow-xs transition-opacity hover:opacity-90"
                  style={{ backgroundColor: "var(--pitch-green)" }}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Ask PlayRef about this Law</span>
                </button>
              </div>

              <h1 className="text-xl sm:text-2xl font-bold tracking-tight" style={{ color: "var(--text-main)" }}>
                {activeLawDetail.title}
              </h1>
            </div>

            {/* Sections List */}
            <div className="space-y-4">
              {activeLawDetail.sections.map((section, idx) => (
                <div
                  key={`${section.chunk_id}-${idx}`}
                  id={section.chunk_id}
                  className="p-5 rounded-2xl border shadow-xs transition-all hover:border-emerald-500/50"
                  style={{
                    backgroundColor: "var(--bg-surface)",
                    borderColor: "var(--border-color)",
                  }}
                >
                  {/* Sticky Section Breadcrumb & Actions */}
                  <div
                    className="flex flex-wrap items-center justify-between gap-2 pb-3 mb-3 border-b"
                    style={{ borderColor: "var(--border-color)" }}
                  >
                    <div className="flex items-center gap-2 text-xs font-semibold" style={{ color: "var(--pitch-green)" }}>
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>{section.section_path || `Section ${idx + 1}`}</span>
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      <span className="opacity-60 text-[11px]">
                        Page {section.page}
                      </span>
                      <button
                        onClick={() =>
                          onAskAboutSection(
                            `Under Law ${activeLawDetail.law_number} (${section.section_path}): ${section.text.slice(0, 160)}... How should a referee interpret this in a match?`
                          )
                        }
                        title={t.lawBrowserView.askAboutSection}
                        className="flex items-center gap-1 px-2.5 py-1 rounded-lg border text-[11px] font-medium opacity-80 hover:opacity-100 hover:border-emerald-600 transition-colors"
                        style={{
                          borderColor: "var(--border-color)",
                          backgroundColor: "var(--bg-tint)",
                          color: "var(--pitch-green)",
                        }}
                      >
                        <HelpCircle className="w-3 h-3" />
                        <span>{t.lawBrowserView.askAboutSection}</span>
                      </button>
                    </div>
                  </div>

                  {/* Rule Text */}
                  <div
                    className="text-sm sm:text-[15px] leading-relaxed whitespace-pre-wrap font-serif sm:font-sans selection:bg-emerald-200"
                    style={{ color: "var(--text-main)" }}
                  >
                    {section.text}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 opacity-60 min-h-[300px]">
            <BookOpen className="w-10 h-10 text-emerald-600" />
            <p className="text-sm font-semibold">{t.lawBrowserView.selectLawPrompt}</p>
          </div>
        )}
      </div>
    </div>
  );
}

