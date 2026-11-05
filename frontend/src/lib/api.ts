/**
 * PlayRef Backend API Client.
 * Handles SSE streaming from FastAPI /chat, retrieval of laws/chunks, and feedback submission.
 */

import {
  AnswerPayload,
  ChunkMetadata,
  ConversationResponse,
  ConversationSummary,
  HealthStatus,
  LanguageCode,
  LawDetail,
  LawSummary,
  StreamDoneEvent,
  StreamRouteEvent,
} from "./types";

export function getApiBase(): string {
  if (typeof window !== "undefined") {
    const envUrl = process.env.NEXT_PUBLIC_API_URL;
    if (envUrl && !envUrl.includes("localhost") && !envUrl.includes("127.0.0.1")) {
      return envUrl;
    }
    const host = window.location.hostname || "localhost";
    return `http://${host}:8000`;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

export interface StreamChatCallbacks {
  onRoute?: (event: StreamRouteEvent) => void;
  onDelta?: (text: string) => void;
  onAnswer?: (answer: AnswerPayload) => void;
  onDone?: (event: StreamDoneEvent) => void;
  onError?: (err: Error) => void;
}

/**
 * Check backend connection and model availability.
 */
export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch(`${getApiBase()}/health`, {
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`Health check failed with status: ${res.status}`);
  }
  return res.json();
}

/**
 * Stream conversational answer from /chat with SSE parsing.
 */
export async function streamChat(
  query: string,
  options: {
    conversationId?: string | null;
    language?: LanguageCode | null;
    signal?: AbortSignal;
    callbacks: StreamChatCallbacks;
  }
): Promise<void> {
  const { conversationId, language, signal, callbacks } = options;

  const res = await fetch(`${getApiBase()}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    },
    body: JSON.stringify({
      query,
      conversation_id: conversationId || undefined,
      stream: true,
      language: language || undefined,
    }),
    signal,
  });

  if (!res.ok) {
    if (res.status === 429) {
      throw new Error("RATE_LIMITED");
    }
    const errText = await res.text().catch(() => "");
    throw new Error(`API error (${res.status}): ${errText || res.statusText}`);
  }

  if (!res.body) {
    throw new Error("No readable response body received from server");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      // Keep incomplete trailing message in buffer
      buffer = lines.pop() || "";

      for (const block of lines) {
        if (!block.trim()) continue;

        let eventType = "message";
        let dataStr = "";

        const subLines = block.split("\n");
        for (const line of subLines) {
          if (line.startsWith("event: ")) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith("data: ")) {
            dataStr = line.slice(6).trim();
          }
        }

        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr);
          if (eventType === "route" && callbacks.onRoute) {
            callbacks.onRoute(parsed);
          } else if (eventType === "delta" && callbacks.onDelta) {
            callbacks.onDelta(parsed.content || "");
          } else if (eventType === "answer" && callbacks.onAnswer) {
            callbacks.onAnswer(parsed);
          } else if (eventType === "done" && callbacks.onDone) {
            callbacks.onDone(parsed);
          }
        } catch {
          // If parse fails for plain string delta
          if (eventType === "delta" && callbacks.onDelta) {
            callbacks.onDelta(dataStr);
          }
        }
      }
    }
  } catch (err: unknown) {
    if ((err as Error)?.name === "AbortError") {
      return;
    }
    if (callbacks.onError) {
      callbacks.onError(err instanceof Error ? err : new Error(String(err)));
    } else {
      throw err;
    }
  }
}

/**
 * List recent conversations.
 */
export async function listConversations(limit = 20): Promise<ConversationSummary[]> {
  const res = await fetch(`${getApiBase()}/conversations?limit=${limit}`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

/**
 * Fetch full conversation history.
 */
export async function getConversation(conversationId: string): Promise<ConversationResponse> {
  const res = await fetch(`${getApiBase()}/conversations/${conversationId}`);
  if (!res.ok) {
    throw new Error(`Conversation ${conversationId} not found`);
  }
  return res.json();
}

/**
 * List all 17 Laws with chunk counts for sidebar / browser.
 */
export async function listLaws(): Promise<LawSummary[]> {
  const res = await fetch(`${getApiBase()}/laws`);
  if (!res.ok) {
    throw new Error("Failed to fetch laws summary");
  }
  return res.json();
}

/**
 * Fetch full details and section chunks for a specific Law.
 */
export async function getLaw(lawNumber: number): Promise<LawDetail> {
  const res = await fetch(`${getApiBase()}/laws/${lawNumber}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch Law ${lawNumber}`);
  }
  return res.json();
}

/**
 * Retrieve exact chunk text and metadata for the citation drawer.
 */
export async function getChunk(chunkId: string): Promise<ChunkMetadata> {
  const res = await fetch(`${getApiBase()}/chunks/${encodeURIComponent(chunkId)}`);
  if (!res.ok) {
    throw new Error(`Chunk ${chunkId} not found`);
  }
  return res.json();
}

/**
 * Submit thumbs up/down or citation defect feedback.
 */
export async function submitFeedback(params: {
  messageId: string;
  rating: number; // 1 or -1
  reason?: string;
  comment?: string;
}): Promise<{ id: string; status: string }> {
  const res = await fetch(`${getApiBase()}/feedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message_id: params.messageId,
      rating: params.rating,
      reason: params.reason || undefined,
      comment: params.comment || undefined,
    }),
  });
  if (!res.ok) {
    throw new Error("Failed to submit feedback");
  }
  return res.json();
}

