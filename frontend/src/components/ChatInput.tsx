"use client";

import React, { useRef, useState } from "react";
import { ArrowUp, Paperclip, Square, X, Image as ImageIcon } from "lucide-react";
import { LanguageCode } from "@/lib/types";
import { translations } from "@/lib/translations";
import { ExperimentalBadge } from "./ExperimentalBadge";

interface ChatInputProps {
  language: LanguageCode;
  onSend: (text: string, mediaFile?: File | null) => void;
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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleFileChange = (file: File) => {
    setSelectedFile(file);
    if (file.type.startsWith("image/")) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      setPreviewUrl(null);
    }
  };

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if ((text.trim() || selectedFile) && !isStreaming && !disabled) {
      onSend(text.trim(), selectedFile);
      setText("");
      handleRemoveFile();
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

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-4">
      {/* Media thumbnail preview */}
      {selectedFile && (
        <div className="mb-2 flex items-center gap-3 p-2 px-3 rounded-xl border bg-white dark:bg-[#16201B] shadow-xs" style={{ borderColor: "var(--border-color)" }}>
          {previewUrl ? (
            /* eslint-disable-next-line @next/next/no-img-element */
            <img
              src={previewUrl}
              alt="Uploaded preview"
              className="w-12 h-12 object-cover rounded-lg border"
              style={{ borderColor: "var(--border-color)" }}
            />
          ) : (
            <div className="w-12 h-12 rounded-lg flex items-center justify-center bg-emerald-100 text-emerald-800">
              <ImageIcon className="w-5 h-5" />
            </div>
          )}

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold truncate text-foreground">
                {selectedFile.name}
              </span>
              <ExperimentalBadge label={t.experimental} size="sm" />
            </div>
            <p className="text-[11px] opacity-60">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • {t.experimentalHelperText}
            </p>
          </div>

          <button
            type="button"
            onClick={handleRemoveFile}
            className="p-1 rounded-lg opacity-60 hover:opacity-100 transition-opacity"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Input Container */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative flex flex-col rounded-2xl border transition-all duration-200 shadow-sm ${
          isDragOver ? "border-dashed border-emerald-500 scale-[1.01]" : ""
        }`}
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: isDragOver ? "var(--pitch-green)" : "var(--border-color)",
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
          {/* Left tools: Upload button with tooltip & badge */}
          <div className="flex items-center gap-2">
            <input
              type="file"
              ref={fileInputRef}
              accept="image/*,video/*"
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files[0]) {
                  handleFileChange(e.target.files[0]);
                }
              }}
            />

            <button
              type="button"
              disabled={disabled || isStreaming}
              onClick={() => fileInputRef.current?.click()}
              title={t.experimentalUploadTooltip}
              className="flex items-center gap-1.5 p-1.5 px-2.5 rounded-xl border text-xs font-medium opacity-70 hover:opacity-100 hover:border-emerald-600 transition-all cursor-pointer disabled:opacity-30"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
              }}
            >
              <Paperclip className="w-4 h-4" />
              <span className="hidden sm:inline-block text-[11px]">Upload</span>
              <ExperimentalBadge label={t.experimental} size="sm" />
            </button>
          </div>

          {/* Right action: Send or Stop */}
          <div className="flex items-center gap-2">
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
                disabled={(!text.trim() && !selectedFile) || disabled}
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

