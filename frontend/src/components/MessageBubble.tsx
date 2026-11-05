"use client";

import React from "react";
import { Message, LanguageCode } from "@/lib/types";
import { AnswerCard } from "./AnswerCard";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: Message;
  language: LanguageCode;
  onOpenCitation: (chunkId: string) => void;
  onClarifyAnswer: (text: string) => void;
  onOpenFeedbackModal: (messageId: string) => void;
}

export function MessageBubble({
  message,
  language,
  onOpenCitation,
  onClarifyAnswer,
  onOpenFeedbackModal,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end w-full mb-5">
        <div className="flex items-start gap-2.5 max-w-[85%] sm:max-w-[70%]">
          <div
            className="p-4 rounded-2xl rounded-tr-xs shadow-xs text-sm sm:text-[15px] leading-relaxed transition-colors"
            style={{
              backgroundColor: "var(--bg-tint)",
              color: "var(--text-main)",
              border: "1px solid rgba(15, 123, 75, 0.2)",
            }}
          >
            {message.content}
          </div>
          <div
            className="w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-1 opacity-80"
            style={{ backgroundColor: "var(--bg-tint)", color: "var(--pitch-green)" }}
          >
            <User className="w-4 h-4" />
          </div>
        </div>
      </div>
    );
  }

  // Assistant Message
  return (
    <div className="flex justify-start w-full mb-6">
      <div className="w-full">
        {message.answer_json ? (
          <AnswerCard
            messageId={message.id}
            answer={message.answer_json}
            language={language}
            onOpenCitation={onOpenCitation}
            onClarifyAnswer={onClarifyAnswer}
            onOpenFeedbackModal={onOpenFeedbackModal}
            isStreaming={message.isStreaming}
          />
        ) : (
          <div
            className="w-full rounded-2xl border p-5 shadow-xs transition-colors"
            style={{
              backgroundColor: "var(--bg-surface)",
              borderColor: "var(--border-color)",
              color: "var(--text-main)",
            }}
          >
            <div className="flex items-center gap-2 mb-2 text-xs font-semibold opacity-70">
              <Bot className="w-4 h-4 text-emerald-600" />
              <span>PlayRef</span>
            </div>
            <p className="text-sm leading-relaxed whitespace-pre-wrap">
              {message.content}
              {message.isStreaming && (
                <span className="inline-block w-2 h-4 ms-1 bg-emerald-600 animate-pulse rounded-xs align-middle" />
              )}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

