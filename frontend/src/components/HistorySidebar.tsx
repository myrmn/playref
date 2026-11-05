"use client";

import React from "react";
import { MessageSquare, Plus, Clock, X } from "lucide-react";
import { ConversationSummary, LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface HistorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  language: LanguageCode;
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
}

export function HistorySidebar({
  isOpen,
  onClose,
  language,
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewChat,
}: HistorySidebarProps) {
  const t = translations[language];

  if (!isOpen) return null;

  return (
    <aside
      className="fixed inset-y-0 start-0 z-40 w-72 flex flex-col border-e shadow-xl transition-transform animate-in duration-200"
      style={{
        backgroundColor: "var(--bg-surface)",
        borderColor: "var(--border-color)",
        color: "var(--text-main)",
      }}
    >
      {/* Header */}
      <div
        className="p-4 border-b flex items-center justify-between"
        style={{ borderColor: "var(--border-color)" }}
      >
        <div className="flex items-center gap-2">
          <Clock className="w-4 h-4 text-emerald-600" />
          <h2 className="text-xs font-bold uppercase tracking-wider">
            {t.recentChats}
          </h2>
        </div>
        <button
          onClick={onClose}
          aria-label="Close sidebar"
          className="p-1 rounded-lg opacity-60 hover:opacity-100 transition-opacity"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* New Chat Button */}
      <div className="p-3">
        <button
          onClick={() => {
            onNewChat();
            onClose();
          }}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 text-xs font-bold rounded-xl text-white shadow-xs transition-transform active:scale-95"
          style={{ backgroundColor: "var(--pitch-green)" }}
        >
          <Plus className="w-4 h-4" />
          <span>{t.newChat}</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {conversations.length === 0 ? (
          <div className="p-6 text-center text-xs opacity-50">
            {t.noRecentChats}
          </div>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <button
                key={conv.id}
                onClick={() => {
                  onSelectConversation(conv.id);
                  onClose();
                }}
                className={`w-full p-2.5 rounded-xl text-start flex items-start gap-2.5 transition-colors ${
                  isActive
                    ? "font-semibold shadow-xs"
                    : "opacity-75 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5"
                }`}
                style={{
                  backgroundColor: isActive ? "var(--bg-tint)" : "transparent",
                  color: isActive ? "var(--pitch-green)" : "var(--text-main)",
                }}
              >
                <MessageSquare className="w-4 h-4 shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-xs truncate font-medium">
                    {conv.title || "Match scenario"}
                  </p>
                  <span className="text-[10px] opacity-60 uppercase">
                    {conv.language}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}

