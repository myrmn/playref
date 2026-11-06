"use client";

import React, { useRef, useState } from "react";
import { ArrowUp, Square } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";

interface ChatInputProps {
  language: LanguageCode;
  onSend: (text: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

export function ChatInput({
  language,
  onSend,
  onStop,
  isStreaming,
  disabled = false,
}: ChatInputProps) {
  const t = translations[language];
  const [text, setText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (text.trim() && !isStreaming && !disabled) {
      onSend(text.trim());
      setText("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    // Auto grow textarea
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 180)}px`;
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      {/* Input Container */}
      <div
        className="relative flex flex-col rounded-2xl border transition-all duration-200 shadow-sm"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-color)",
        }}
      >
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          disabled={disabled || isStreaming}
          onChange={handleTextChange}
          onKeyDown={handleKeyDown}
          placeholder={t.inputPlaceholder}
          className="w-full px-4 pt-3.5 pb-2 text-sm sm:text-[15px] bg-transparent resize-none focus:outline-none transition-colors"
          style={{ color: "var(--text-main)" }}
        />

        {/* Action Toolbar */}
        <div className="flex items-center justify-between px-3 pb-2.5 pt-1">
          {/* Helpful suggestion hint */}
          <div className="text-[11px] opacity-50 px-1 hidden sm:block select-none" style={{ color: "var(--text-muted)" }}>
            Press Enter to ask PlayRef
          </div>

          {/* Right action: Send or Stop */}
          <div className="flex items-center gap-2 ms-auto">
            {isStreaming ? (
              <button
                type="button"
                onClick={onStop}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold text-white shadow-xs transition-opacity hover:opacity-90"
                style={{ backgroundColor: "var(--card-red)" }}
              >
                <Square className="w-3.5 h-3.5 fill-current" />
                <span>{t.stop}</span>
              </button>
            ) : (
              <button
                type="button"
                disabled={!text.trim() || disabled}
                onClick={() => handleSubmit()}
                className="flex items-center justify-center w-8 h-8 rounded-xl text-white shadow-xs transition-all active:scale-95 disabled:opacity-30 disabled:scale-100"
                style={{ backgroundColor: "var(--pitch-green)" }}
                aria-label={t.send}
              >
                <ArrowUp className="w-4 h-4 stroke-[2.5]" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
