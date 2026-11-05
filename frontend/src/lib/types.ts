/**
 * PlayRef TypeScript type definitions.
 * Matches backend schemas in backend/app/api/schemas.py and docs/PROJECT_SPEC.md.
 */

export type LanguageCode = "en" | "fr" | "ar";

export interface ApplicableLaw {
  citation: string;
  chunk_id: string;
  quote_or_summary?: string;
}

export interface AnswerPayload {
  short_answer: string;
  applicable_laws: ApplicableLaw[];
  interpretations: string[];
  what_would_change_the_decision: string[];
  assumptions: string[];
  needs_more_info: boolean;
  clarifying_question: string | null;
  language: string;
}

export interface Message {
  id: string;
  conversation_id?: string;
  role: "user" | "assistant";
  content: string;
  answer_json?: AnswerPayload | null;
  retrieved_chunk_ids?: string[];
  created_at?: string;
  isStreaming?: boolean;
  streamingStage?: string;
}

export interface ConversationSummary {
  id: string;
  created_at: string;
  language: string;
  title: string | null;
}

export interface ConversationResponse {
  id: string;
  created_at: string;
  language: string;
  title: string | null;
  messages: Message[];
}

export interface ChunkMetadata {
  chunk_id: string;
  law_number: number;
  law_title: string;
  section_path: string;
  edition: string;
  page: number;
  source: string;
  clean_text: string;
  lang: string;
}

export interface LawSummary {
  law_number: number;
  title: string;
  chunk_count: number;
}

export interface LawSectionItem {
  chunk_id: string;
  section_path: string;
  page: number;
  text: string;
}

export interface LawDetail {
  law_number: number;
  title: string;
  edition: string;
  sections: LawSectionItem[];
}

export interface HealthStatus {
  status: string;
  edition: string;
  models: Record<string, string>;
  qdrant: string;
}

export interface StreamDeltaEvent {
  content: string;
}

export interface StreamRouteEvent {
  intent: string;
  lang: string;
  duration_ms?: number;
}

export interface StreamDoneEvent {
  timings?: Record<string, number>;
  total_ms?: number;
  conversation_id?: string;
  message_id?: string;
}

