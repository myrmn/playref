"use client";

import React from "react";
import { BookOpen, MessageSquare, Moon, Sun, CheckCircle2, AlertCircle, Menu, X } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface HeaderProps {
  currentLanguage: LanguageCode;
  onLanguageChange: (lang: LanguageCode) => void;
  activeView: "chat" | "laws";
  onViewChange: (view: "chat" | "laws") => void;
  isDark: boolean;
  onToggleTheme: () => void;
  isBackendConnected: boolean;
  onToggleHistory?: () => void;
  isHistoryOpen?: boolean;
}

export function Header({
  currentLanguage,
  onLanguageChange,
  activeView,
  onViewChange,
  isDark,
  onToggleTheme,
  isBackendConnected,
  onToggleHistory,
  isHistoryOpen,
}: HeaderProps) {
  const t = translations[currentLanguage];

  return (
    <header
      className="sticky top-0 z-30 w-full border-b backdrop-blur-md transition-colors"
      style={{
        backgroundColor: isDark ? "rgba(22, 32, 27, 0.85)" : "rgba(255, 255, 255, 0.88)",
        borderColor: "var(--border-color)",
      }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-4">
        {/* Left: Brand Logo & Navigation */}
        <div className="flex items-center gap-4 sm:gap-6">
          {onToggleHistory && (
            <button
              onClick={onToggleHistory}
              aria-label="Toggle history"
              className="p-2 rounded-lg sm:hidden hover:opacity-80 transition-opacity"
              style={{ color: "var(--text-main)" }}
            >
              {isHistoryOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          )}

          <div
            onClick={() => onViewChange("chat")}
            className="flex items-center gap-2.5 cursor-pointer select-none group"
          >
            {/* Minimal pitch-mark logo badge */}
            <div
              className="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-white shadow-sm transition-transform group-hover:scale-105"
              style={{ backgroundColor: "var(--pitch-green)" }}
            >
              <svg
                viewBox="0 0 24 24"
                className="w-5 h-5 stroke-current fill-none stroke-[2.2]"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                {/* Football pitch rectangle & center circle */}
                <rect x="3" y="4" width="18" height="16" rx="2" />
                <line x1="12" y1="4" x2="12" y2="20" />
                <circle cx="12" cy="12" r="3" />
              </svg>
            </div>
            <div className="flex flex-col">
              <span className="font-bold text-lg leading-tight tracking-tight" style={{ color: "var(--text-main)" }}>
                PlayRef
              </span>
              <span className="text-[10px] hidden sm:inline-block leading-none" style={{ color: "var(--text-muted)" }}>
                IFAB Laws of the Game
              </span>
            </div>
          </div>

          {/* View Tabs */}
          <nav className="flex items-center gap-1 bg-opacity-50 p-1 rounded-xl" style={{ backgroundColor: "var(--bg-app)" }}>
            <button
              onClick={() => onViewChange("chat")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
                activeView === "chat"
                  ? "bg-white dark:bg-[#16201B] shadow-sm font-semibold"
                  : "text-muted hover:text-foreground opacity-70 hover:opacity-100"
              }`}
              style={{
                color: activeView === "chat" ? "var(--pitch-green)" : "var(--text-muted)",
              }}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Chat</span>
            </button>
            <button
              onClick={() => onViewChange("laws")}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all ${
                activeView === "laws"
                  ? "bg-white dark:bg-[#16201B] shadow-sm font-semibold"
                  : "text-muted hover:text-foreground opacity-70 hover:opacity-100"
              }`}
              style={{
                color: activeView === "laws" ? "var(--pitch-green)" : "var(--text-muted)",
              }}
            >
              <BookOpen className="w-4 h-4" />
              <span>{t.lawBrowser}</span>
            </button>
          </nav>
        </div>

        {/* Right: Controls (Backend Status, Language Selector, Dark Mode) */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Connection status pill */}
          <div
            className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border"
            style={{
              backgroundColor: isBackendConnected ? "var(--bg-tint)" : "var(--card-red-bg)",
              borderColor: isBackendConnected ? "rgba(15, 123, 75, 0.2)" : "rgba(215, 38, 61, 0.2)",
              color: isBackendConnected ? "var(--pitch-green)" : "var(--card-red)",
            }}
            title={isBackendConnected ? t.status.connected : t.status.error}
          >
            {isBackendConnected ? (
              <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
            ) : (
              <AlertCircle className="w-3.5 h-3.5 shrink-0" />
            )}
            <span className="text-[11px] truncate max-w-[120px]">
              {isBackendConnected ? t.status.connected : t.status.error}
            </span>
          </div>

          {/* Language Switcher */}
          <div className="flex items-center rounded-lg border p-0.5 text-xs font-semibold" style={{ borderColor: "var(--border-color)", backgroundColor: "var(--bg-surface)" }}>
            {(["en", "fr", "ar"] as LanguageCode[]).map((lang) => (
              <button
                key={lang}
                onClick={() => onLanguageChange(lang)}
                className={`px-2 py-1 rounded-md uppercase tracking-wider transition-all ${
                  currentLanguage === lang
                    ? "text-white font-bold shadow-xs"
                    : "opacity-60 hover:opacity-100"
                }`}
                style={{
                  backgroundColor: currentLanguage === lang ? "var(--pitch-green)" : "transparent",
                  color: currentLanguage === lang ? "#FFFFFF" : "var(--text-main)",
                }}
              >
                {lang}
              </button>
            ))}
          </div>

          {/* Theme Toggle */}
          <button
            onClick={onToggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-lg border hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
            style={{
              borderColor: "var(--border-color)",
              color: "var(--text-main)",
              backgroundColor: "var(--bg-surface)",
            }}
          >
            {isDark ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>
    </header>
  );
}

