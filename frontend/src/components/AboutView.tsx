"use client";

import React from "react";
import {
  BookOpen,
  CheckCircle2,
  Globe,
  HelpCircle,
  MessageSquare,
  Scale,
  ShieldAlert,
  Sparkles,
  ArrowRight,
} from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface AboutViewProps {
  language: LanguageCode;
  onNavigate: (view: "chat" | "laws") => void;
}

export function AboutView({ language, onNavigate }: AboutViewProps) {
  const t = translations[language];
  const { aboutView } = t;

  return (
    <div className="flex-1 overflow-y-auto px-4 py-8 sm:py-12">
      <div className="max-w-4xl mx-auto space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <div
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold shadow-xs"
            style={{
              backgroundColor: "var(--bg-tint)",
              color: "var(--pitch-green)",
              border: "1px solid rgba(15, 123, 75, 0.2)",
            }}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{aboutView.badge}</span>
          </div>

          <h1
            className="text-3xl sm:text-5xl font-extrabold tracking-tight"
            style={{ color: "var(--text-main)" }}
          >
            {aboutView.title}
          </h1>

          <p
            className="text-base sm:text-lg max-w-2xl mx-auto leading-relaxed opacity-80"
            style={{ color: "var(--text-muted)" }}
          >
            {aboutView.subtitle}
          </p>

          <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
            <button
              onClick={() => onNavigate("chat")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-bold text-sm text-white shadow-sm transition-all hover:opacity-90 active:scale-95"
              style={{ backgroundColor: "var(--pitch-green)" }}
            >
              <span>{aboutView.ctaButton}</span>
              <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            </button>
            <button
              onClick={() => onNavigate("laws")}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl font-semibold text-sm border shadow-xs transition-colors hover:bg-black/5 dark:hover:bg-white/5"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
                backgroundColor: "var(--bg-surface)",
              }}
            >
              <BookOpen className="w-4 h-4 text-emerald-600" />
              <span>{aboutView.browseLawsBtn}</span>
            </button>
          </div>
        </div>

        {/* Why Does PlayRef Exist Card */}
        <div
          className="rounded-2xl border p-6 sm:p-8 shadow-xs transition-colors"
          style={{
            backgroundColor: "var(--bg-surface)",
            borderColor: "var(--border-color)",
          }}
        >
          <div className="flex items-center gap-2.5 mb-3">
            <div
              className="w-9 h-9 rounded-xl flex items-center justify-center"
              style={{
                backgroundColor: "var(--bg-tint)",
                color: "var(--pitch-green)",
              }}
            >
              <HelpCircle className="w-5 h-5" />
            </div>
            <h2 className="text-lg sm:text-xl font-bold" style={{ color: "var(--text-main)" }}>
              {aboutView.whatIsPlayRef}
            </h2>
          </div>
          <p
            className="text-sm sm:text-base leading-relaxed opacity-85"
            style={{ color: "var(--text-muted)" }}
          >
            {aboutView.whatIsPlayRefDesc}
          </p>
        </div>

        {/* 4 Feature Pillars Grid */}
        <div className="space-y-4">
          <h2
            className="text-xl sm:text-2xl font-bold tracking-tight text-center sm:text-start"
            style={{ color: "var(--text-main)" }}
          >
            {aboutView.featuresTitle}
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Feature 1 */}
            <div
              className="rounded-2xl border p-5 sm:p-6 shadow-xs flex flex-col justify-between"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="space-y-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{
                    backgroundColor: "var(--bg-tint)",
                    color: "var(--pitch-green)",
                  }}
                >
                  <MessageSquare className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base" style={{ color: "var(--text-main)" }}>
                  {aboutView.feature1Title}
                </h3>
                <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {aboutView.feature1Desc}
                </p>
              </div>
            </div>

            {/* Feature 2 */}
            <div
              className="rounded-2xl border p-5 sm:p-6 shadow-xs flex flex-col justify-between"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="space-y-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400"
                >
                  <BookOpen className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base" style={{ color: "var(--text-main)" }}>
                  {aboutView.feature2Title}
                </h3>
                <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {aboutView.feature2Desc}
                </p>
              </div>
            </div>

            {/* Feature 3 */}
            <div
              className="rounded-2xl border p-5 sm:p-6 shadow-xs flex flex-col justify-between"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="space-y-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-50 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400"
                >
                  <Scale className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base" style={{ color: "var(--text-main)" }}>
                  {aboutView.feature3Title}
                </h3>
                <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {aboutView.feature3Desc}
                </p>
              </div>
            </div>

            {/* Feature 4 */}
            <div
              className="rounded-2xl border p-5 sm:p-6 shadow-xs flex flex-col justify-between"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="space-y-3">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400"
                >
                  <Globe className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-base" style={{ color: "var(--text-main)" }}>
                  {aboutView.feature4Title}
                </h3>
                <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                  {aboutView.feature4Desc}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* How It Works in 3 Steps */}
        <div className="space-y-4">
          <h2
            className="text-xl sm:text-2xl font-bold tracking-tight text-center sm:text-start"
            style={{ color: "var(--text-main)" }}
          >
            {aboutView.howItWorksTitle}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div
              className="rounded-2xl border p-5 shadow-xs relative"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                  style={{ backgroundColor: "var(--pitch-green)" }}
                >
                  1
                </span>
                <h4 className="font-bold text-sm" style={{ color: "var(--text-main)" }}>
                  {aboutView.step1Title}
                </h4>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                {aboutView.step1Desc}
              </p>
            </div>

            <div
              className="rounded-2xl border p-5 shadow-xs relative"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                  style={{ backgroundColor: "var(--pitch-green)" }}
                >
                  2
                </span>
                <h4 className="font-bold text-sm" style={{ color: "var(--text-main)" }}>
                  {aboutView.step2Title}
                </h4>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                {aboutView.step2Desc}
              </p>
            </div>

            <div
              className="rounded-2xl border p-5 shadow-xs relative"
              style={{
                backgroundColor: "var(--bg-surface)",
                borderColor: "var(--border-color)",
              }}
            >
              <div className="flex items-center gap-2 mb-2">
                <span
                  className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
                  style={{ backgroundColor: "var(--pitch-green)" }}
                >
                  3
                </span>
                <h4 className="font-bold text-sm" style={{ color: "var(--text-main)" }}>
                  {aboutView.step3Title}
                </h4>
              </div>
              <p className="text-xs sm:text-sm leading-relaxed" style={{ color: "var(--text-muted)" }}>
                {aboutView.step3Desc}
              </p>
            </div>
          </div>
        </div>

        {/* Friendly Referee Notice */}
        <div
          className="rounded-2xl border p-5 sm:p-6 flex items-start gap-4 shadow-xs"
          style={{
            backgroundColor: "var(--referee-yellow-bg)",
            borderColor: "var(--referee-yellow-border)",
          }}
        >
          <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0 text-amber-800 bg-amber-100">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <h3 className="font-bold text-sm text-amber-900 dark:text-amber-300">
              {aboutView.refereeNoticeTitle}
            </h3>
            <p className="text-xs sm:text-sm leading-relaxed text-amber-800 dark:text-amber-400">
              {aboutView.refereeNoticeDesc}
            </p>
          </div>
        </div>

        {/* Bottom CTA Card */}
        <div
          className="rounded-3xl p-8 sm:p-10 text-center text-white space-y-4 shadow-lg"
          style={{
            backgroundColor: "var(--pitch-green)",
            backgroundImage: "radial-gradient(circle at top right, rgba(255,255,255,0.15), transparent 70%)",
          }}
        >
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
            Ready to test your football knowledge?
          </h2>
          <p className="text-sm sm:text-base max-w-lg mx-auto opacity-90 leading-relaxed">
            Ask any question right now and discover what the official Laws of the Game say.
          </p>
          <div className="pt-2">
            <button
              onClick={() => onNavigate("chat")}
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold text-sm bg-white text-emerald-900 shadow-md hover:bg-emerald-50 transition-all active:scale-95"
            >
              <span>{aboutView.ctaButton}</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

