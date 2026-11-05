"use client";

import { useState, useEffect } from "react";

export function useTheme() {
  const [isDark, setIsDark] = useState<boolean>(false);
  const [mounted, setMounted] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    Promise.resolve().then(() => {
      if (!isMounted) return;
      setMounted(true);
      const saved = localStorage.getItem("playref-theme");
      if (saved) {
        setIsDark(saved === "dark");
      } else if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: dark)").matches) {
        setIsDark(true);
      }
    });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (!mounted) return;
    if (isDark) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDark, mounted]);

  const toggleTheme = () => {
    setIsDark((prev) => {
      const next = !prev;
      if (typeof window !== "undefined") {
        localStorage.setItem("playref-theme", next ? "dark" : "light");
      }
      return next;
    });
  };

  return { isDark, toggleTheme };
}
