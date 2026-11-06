"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { AboutView } from "@/components/AboutView";
import { DisclaimerFooter } from "@/components/DisclaimerFooter";
import { useTheme } from "@/hooks/useTheme";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

export default function AboutPage() {
  const router = useRouter();
  const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>("en");
  const { isDark, toggleTheme } = useTheme();

  // Direction sync (LTR for en/fr, RTL for ar)
  useEffect(() => {
    document.documentElement.dir = currentLanguage === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage]);

  const t = translations[currentLanguage];

  const handleNavigate = (view: "chat" | "laws" | "about") => {
    if (view === "chat") {
      router.push("/");
    } else if (view === "laws") {
      router.push("/?view=laws");
    }
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      <Header
        currentLanguage={currentLanguage}
        onLanguageChange={setCurrentLanguage}
        activeView="about"
        onViewChange={handleNavigate}
        isDark={isDark}
        onToggleTheme={toggleTheme}
        isBackendConnected={true}
      />

      <main className="flex-1 flex flex-col relative overflow-hidden">
        <AboutView language={currentLanguage} onNavigate={handleNavigate} />
      </main>

      <DisclaimerFooter text={t.disclaimer} />
    </div>
  );
}

