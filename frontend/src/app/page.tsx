"use client";

import React, { useEffect, useRef, useState } from "react";
import { AlertCircle, AlertTriangle, RefreshCw, Scale } from "lucide-react";
import { Header } from "@/components/Header";
import { SuggestedPrompts } from "@/components/SuggestedPrompts";
import { MessageBubble } from "@/components/MessageBubble";
import { ChatInput } from "@/components/ChatInput";
import { StageIndicator } from "@/components/StageIndicator";
import { CitationDrawer } from "@/components/CitationDrawer";
import { FeedbackModal } from "@/components/FeedbackModal";
import { LawBrowser } from "@/components/LawBrowser";
import { HistorySidebar } from "@/components/HistorySidebar";
import { DisclaimerFooter } from "@/components/DisclaimerFooter";
import { useChat } from "@/hooks/useChat";
import { useTheme } from "@/hooks/useTheme";
import { fetchHealth, listConversations } from "@/lib/api";
import { ConversationSummary, LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

export default function Home() {
  const [currentLanguage, setCurrentLanguage] = useState<LanguageCode>("en");
  const [activeView, setActiveView] = useState<"chat" | "laws">("chat");
  const [selectedLawNumber, setSelectedLawNumber] = useState<number | null>(null);

  // Modals & Drawers
  const [activeCitationChunkId, setActiveCitationChunkId] = useState<string | null>(null);
  const [feedbackMessageId, setFeedbackMessageId] = useState<string | null>(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);

  // Backend status & conversations
  const [isBackendConnected, setIsBackendConnected] = useState(true);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);

  const { isDark, toggleTheme } = useTheme();
  const {
    messages,
    conversationId,
    isStreaming,
    streamingStage,
    rateLimited,
    generalError,
    sendMessage,
    stopStreaming,
    loadConversation,
    newChat,
  } = useChat(currentLanguage);

  const t = translations[currentLanguage];
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Direction sync (LTR for en/fr, RTL for ar)
  useEffect(() => {
    document.documentElement.dir = currentLanguage === "ar" ? "rtl" : "ltr";
    document.documentElement.lang = currentLanguage;
  }, [currentLanguage]);

  // Initial Health check & recent conversations load
  useEffect(() => {
    fetchHealth()
      .then(() => setIsBackendConnected(true))
      .catch(() => setIsBackendConnected(false));

    listConversations()
      .then((data) => setConversations(data))
      .catch(() => {});
  }, [conversationId]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (activeView === "chat") {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, streamingStage, activeView]);

  const handleLanguageChange = (lang: LanguageCode) => {
    setCurrentLanguage(lang);
  };

  const handleOpenCitation = (chunkId: string) => {
    setActiveCitationChunkId(chunkId);
  };

  const handleOpenInLawBrowser = (lawNumber: number) => {
    setSelectedLawNumber(lawNumber);
    setActiveView("laws");
  };

  const handleAskAboutSection = (promptText: string) => {
    setActiveView("chat");
    sendMessage(promptText, null, currentLanguage);
  };

  return (
    <div className="min-h-screen flex flex-col transition-colors duration-200">
      {/* Top Navigation */}
      <Header
        currentLanguage={currentLanguage}
        onLanguageChange={handleLanguageChange}
        activeView={activeView}
        onViewChange={setActiveView}
        isDark={isDark}
        onToggleTheme={toggleTheme}
        isBackendConnected={isBackendConnected}
        onToggleHistory={() => setIsHistoryOpen(!isHistoryOpen)}
        isHistoryOpen={isHistoryOpen}
      />

      {/* History Sidebar */}
      <HistorySidebar
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        language={currentLanguage}
        conversations={conversations}
        activeConversationId={conversationId}
        onSelectConversation={(id) => {
          loadConversation(id);
          setActiveView("chat");
        }}
        onNewChat={newChat}
      />

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden">
        {activeView === "laws" ? (
          <LawBrowser
            language={currentLanguage}
            selectedLawNumber={selectedLawNumber}
            onSelectLawNumber={setSelectedLawNumber}
            onAskAboutSection={handleAskAboutSection}
          />
        ) : (
          <div className="flex-1 flex flex-col justify-between">
            {/* Rate limit warning banner (Screen 10) */}
            {rateLimited && (
              <div
                className="w-full max-w-4xl mx-auto mt-4 px-4 py-3 rounded-xl border flex items-center gap-3 text-xs font-semibold shadow-xs"
                style={{
                  backgroundColor: "var(--referee-yellow-bg)",
                  borderColor: "var(--referee-yellow-border)",
                  color: "#926800",
                }}
              >
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{t.status.rateLimited}</span>
              </div>
            )}

            {/* General error banner with retry */}
            {generalError && (
              <div
                className="w-full max-w-4xl mx-auto mt-4 px-4 py-3 rounded-xl border flex items-center justify-between gap-3 text-xs font-semibold shadow-xs"
                style={{
                  backgroundColor: "var(--card-red-bg)",
                  borderColor: "var(--card-red-border)",
                  color: "var(--card-red)",
                }}
              >
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{generalError}</span>
                </div>
                <button
                  onClick={() => {
                    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
                    if (lastUserMsg) sendMessage(lastUserMsg.content, null, currentLanguage);
                  }}
                  className="flex items-center gap-1 underline cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>Retry</span>
                </button>
              </div>
            )}

            {/* Empty Chat / Home Screen (Screen 1) */}
            {messages.length === 0 ? (
              <div className="flex-1 flex flex-col items-center justify-center py-10 px-4 text-center">
                {/* Hero Pitch Icon */}
                <div
                  className="w-16 h-16 rounded-3xl flex items-center justify-center mb-6 shadow-md"
                  style={{
                    backgroundColor: "var(--bg-tint)",
                    color: "var(--pitch-green)",
                  }}
                >
                  <Scale className="w-8 h-8 stroke-[2.2]" />
                </div>

                {/* Headline and Subline */}
                <h1
                  className="text-2xl sm:text-4xl font-extrabold tracking-tight mb-3 max-w-2xl"
                  style={{ color: "var(--text-main)" }}
                >
                  {t.homeHeadline}
                </h1>
                <p
                  className="text-sm sm:text-base max-w-xl mx-auto leading-relaxed mb-8 opacity-75"
                  style={{ color: "var(--text-muted)" }}
                >
                  {t.homeSubline}
                </p>

                {/* Suggested Prompts 2x3 Grid */}
                <SuggestedPrompts
                  currentLanguage={currentLanguage}
                  onSelectPrompt={(prompt) => sendMessage(prompt, null, currentLanguage)}
                />
              </div>
            ) : (
              /* Active Conversation Screen (Screen 2) */
              <div className="flex-1 overflow-y-auto px-4 py-6">
                <div className="max-w-4xl mx-auto w-full">
                  {messages.map((msg) => (
                    <MessageBubble
                      key={msg.id}
                      message={msg}
                      language={currentLanguage}
                      onOpenCitation={handleOpenCitation}
                      onClarifyAnswer={(text) => sendMessage(text, null, currentLanguage)}
                      onOpenFeedbackModal={setFeedbackMessageId}
                    />
                  ))}

                  {/* Stage indicator while streaming */}
                  {isStreaming && (
                    <StageIndicator
                      stage={streamingStage}
                      language={currentLanguage}
                      onStop={stopStreaming}
                    />
                  )}

                  <div ref={messagesEndRef} />
                </div>
              </div>
            )}

            {/* Sticky Chat Input at Bottom */}
            <div
              className="sticky bottom-0 z-20 pt-2 transition-colors"
              style={{
                backgroundColor: isDark
                  ? "rgba(14, 21, 18, 0.95)"
                  : "rgba(248, 250, 249, 0.95)",
              }}
            >
              <ChatInput
                language={currentLanguage}
                onSend={(text, file) => sendMessage(text, file, currentLanguage)}
                onStop={stopStreaming}
                isStreaming={isStreaming}
              />
            </div>
          </div>
        )}
      </main>

      {/* Citation Slide-over Drawer (Screen 3 & 9) */}
      <CitationDrawer
        chunkId={activeCitationChunkId}
        isOpen={Boolean(activeCitationChunkId)}
        language={currentLanguage}
        onClose={() => setActiveCitationChunkId(null)}
        onOpenInLawBrowser={handleOpenInLawBrowser}
      />

      {/* "Wrong law cited" Feedback Modal (Screen 11) */}
      <FeedbackModal
        isOpen={Boolean(feedbackMessageId)}
        messageId={feedbackMessageId || ""}
        language={currentLanguage}
        onClose={() => setFeedbackMessageId(null)}
        onSubmit={async (data) => {
          const { submitFeedback } = await import("@/lib/api");
          await submitFeedback(data);
        }}
      />

      {/* Mandatory Disclaimer Footer */}
      <DisclaimerFooter text={t.disclaimer} />
    </div>
  );
}
