import { useState, useRef, useCallback } from "react";
import { Message, LanguageCode, AnswerPayload, StreamDoneEvent } from "@/lib/types";
import { streamChat, getConversation } from "@/lib/api";

export function useChat(initialLanguage: LanguageCode = "en") {
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingStage, setStreamingStage] = useState<string>("");
  const [rateLimited, setRateLimited] = useState(false);
  const [generalError, setGeneralError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsStreaming(false);
    setStreamingStage("");
  }, []);

  const sendMessage = useCallback(
    async (query: string, mediaFile?: File | null, language?: LanguageCode) => {
      if (!query.trim() && !mediaFile) return;

      setRateLimited(false);
      setGeneralError(null);

      // If user provided a media file, prepend a note about the uploaded media
      const userText = mediaFile
        ? `[Attached ${mediaFile.name} (${(mediaFile.size / 1024).toFixed(0)} KB)]\n${query}`
        : query;

      const userMsgId = `user-${Date.now()}`;
      const botMsgId = `bot-${Date.now()}`;

      const userMsg: Message = {
        id: userMsgId,
        conversation_id: conversationId || undefined,
        role: "user",
        content: userText,
        created_at: new Date().toISOString(),
      };

      const botMsg: Message = {
        id: botMsgId,
        conversation_id: conversationId || undefined,
        role: "assistant",
        content: "",
        isStreaming: true,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMsg, botMsg]);
      setIsStreaming(true);
      setStreamingStage("routing");

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      let accumulatedDelta = "";

      try {
        await streamChat(query, {
          conversationId,
          language: language || initialLanguage,
          signal: abortController.signal,
          callbacks: {
            onRoute: () => {
              setStreamingStage("searching");
            },
            onDelta: (chunkText: string) => {
              accumulatedDelta += chunkText;
              setStreamingStage("writing");
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId
                    ? { ...m, content: accumulatedDelta }
                    : m
                )
              );
            },
            onAnswer: (answerPayload: AnswerPayload) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === botMsgId
                    ? {
                        ...m,
                        content: answerPayload.short_answer,
                        answer_json: answerPayload,
                      }
                    : m
                )
              );
            },
            onDone: (doneEvt: StreamDoneEvent) => {
              setIsStreaming(false);
              setStreamingStage("");
              if (doneEvt.conversation_id) {
                setConversationId(doneEvt.conversation_id);
              }
              if (doneEvt.message_id) {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === botMsgId ? { ...m, id: doneEvt.message_id!, isStreaming: false } : m
                  )
                );
              } else {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === botMsgId ? { ...m, isStreaming: false } : m
                  )
                );
              }
            },
            onError: (err: Error) => {
              setIsStreaming(false);
              setStreamingStage("");
              if (err.message === "RATE_LIMITED") {
                setRateLimited(true);
              } else {
                setGeneralError(err.message || "An error occurred");
              }
            },
          },
        });
      } catch (err: unknown) {
        setIsStreaming(false);
        setStreamingStage("");
        const errMsg = err instanceof Error ? err.message : String(err);
        if (errMsg === "RATE_LIMITED") {
          setRateLimited(true);
        } else {
          setGeneralError(errMsg || "Failed to communicate with PlayRef backend");
        }
      }
    },
    [conversationId, initialLanguage]
  );

  const loadConversation = useCallback(async (id: string) => {
    try {
      const conv = await getConversation(id);
      setConversationId(conv.id);
      setMessages(conv.messages || []);
      setGeneralError(null);
    } catch (err: unknown) {
      setGeneralError(err instanceof Error ? err.message : "Failed to load conversation");
    }
  }, []);

  const newChat = useCallback(() => {
    stopStreaming();
    setConversationId(null);
    setMessages([]);
    setRateLimited(false);
    setGeneralError(null);
  }, [stopStreaming]);

  return {
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
    setMessages,
  };
}

