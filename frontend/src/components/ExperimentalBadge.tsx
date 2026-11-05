import React from "react";
import { FlaskConical } from "lucide-react";

interface ExperimentalBadgeProps {
  label?: string;
  size?: "sm" | "md";
  className?: string;
}

export function ExperimentalBadge({
  label = "Experimental",
  size = "sm",
  className = "",
}: ExperimentalBadgeProps) {
  const sizeClasses =
    size === "sm" ? "text-xs px-2 py-0.5 gap-1" : "text-sm px-2.5 py-1 gap-1.5";

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border transition-colors ${sizeClasses} ${className}`}
      style={{
        backgroundColor: "var(--referee-yellow-bg)",
        borderColor: "var(--referee-yellow-border)",
        color: "#926800",
      }}
    >
      <FlaskConical className="w-3 h-3 stroke-[1.8]" />
      <span>{label}</span>
    </span>
  );
}

