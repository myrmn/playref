"use client";

import React, { useState } from "react";
import { Lock, Sparkles, X, Check, ArrowRight } from "lucide-react";
import { LanguageCode } from "@/lib/types";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (email: string) => void;
  language: LanguageCode;
}

export function AuthModal({
  isOpen,
  onClose,
  onLoginSuccess,
  language,
}: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  if (!isOpen) return null;

  const isArabic = language === "ar";
  const isFrench = language === "fr";

  const t = {
    title: isArabic
      ? "استنفدت أسئلتك الـ 5 المجانية!"
      : isFrench
      ? "Vous avez utilisé vos 5 questions gratuites !"
      : "You've used your 5 free guest questions!",
    subtitle: isArabic
      ? "سجّل دخولك الآن للاستمتاع بأسئلة غير محدودة وحفظ نقاشاتك التحكيمية السابقة."
      : isFrench
      ? "Connectez-vous pour profiter d'un nombre illimité de questions et sauvegarder votre historique."
      : "Sign in to unlock unlimited questions, save your match chats, and explore the Laws without limits.",
    google: isArabic ? "المتابعة باستخدام Google" : isFrench ? "Continuer avec Google" : "Continue with Google",
    or: isArabic ? "أو باستخدام البريد الإلكتروني" : isFrench ? "ou avec votre e-mail" : "or with email",
    emailPlaceholder: isArabic ? "بريدك الإلكتروني" : isFrench ? "Votre adresse e-mail" : "Your email address",
    passwordPlaceholder: isArabic ? "كلمة المرور" : isFrench ? "Mot de passe" : "Password",
    signInBtn: isArabic ? "تسجيل الدخول" : isFrench ? "Se connecter" : "Sign In",
    signUpBtn: isArabic ? "إنشاء حساب مجاني" : isFrench ? "Créer un compte gratuit" : "Create Free Account",
    demoBtn: isArabic ? "دخول تجريبي بنقرة واحدة (Demo)" : isFrench ? "Connexion démo en 1 clic" : "1-Click Demo Login",
    haveAccount: isArabic ? "لديك حساب بالفعل؟" : isFrench ? "Déjà un compte ?" : "Already have an account?",
    noAccount: isArabic ? "ليس لديك حساب؟" : isFrench ? "Pas encore de compte ?" : "Don't have an account?",
    switchSignIn: isArabic ? "سجل الدخول" : isFrench ? "Se connecter" : "Sign in",
    switchSignUp: isArabic ? "أنشئ حساباً مجاناً" : isFrench ? "Créer un compte" : "Sign up free",
    perk1: isArabic ? "أسئلة غير محدودة عن قوانين IFAB" : isFrench ? "Questions illimitées sur les Lois IFAB" : "Unlimited questions on IFAB Laws",
    perk2: isArabic ? "حفظ واسترجاع سجل استفساراتك" : isFrench ? "Historique des discussions sauvegardé" : "Save and revisit your rule debates",
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const userEmail = email.trim() || "referee.fan@playref.io";
    onLoginSuccess(userEmail);
  };

  const handleGoogleLogin = () => {
    onLoginSuccess("google.user@playref.io");
  };

  const handleDemoLogin = () => {
    onLoginSuccess("demo.fan@playref.io");
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div
        className="relative w-full max-w-md rounded-3xl border p-6 sm:p-8 shadow-2xl transition-all"
        style={{
          backgroundColor: "var(--bg-surface)",
          borderColor: "var(--border-color)",
          color: "var(--text-main)",
        }}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          aria-label="Close"
          className="absolute top-5 end-5 p-1.5 rounded-full opacity-60 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5 transition-all"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header Icon */}
        <div className="flex flex-col items-center text-center space-y-3 mb-6">
          <div
            className="w-12 h-12 rounded-2xl flex items-center justify-center shadow-md"
            style={{
              backgroundColor: "var(--bg-tint)",
              color: "var(--pitch-green)",
            }}
          >
            <Lock className="w-6 h-6 stroke-[2.2]" />
          </div>

          <h3 className="text-xl sm:text-2xl font-extrabold tracking-tight">
            {t.title}
          </h3>

          <p className="text-xs sm:text-sm leading-relaxed opacity-75 max-w-xs">
            {t.subtitle}
          </p>

          {/* Member perks */}
          <div className="w-full pt-1 space-y-1.5 text-xs text-start">
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-medium">
              <Check className="w-4 h-4 shrink-0" />
              <span>{t.perk1}</span>
            </div>
            <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-medium">
              <Check className="w-4 h-4 shrink-0" />
              <span>{t.perk2}</span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="space-y-3">
          {/* 1-Click Demo Login */}
          <button
            type="button"
            onClick={handleDemoLogin}
            className="w-full py-2.5 px-4 rounded-xl font-bold text-xs sm:text-sm text-white shadow-sm flex items-center justify-center gap-2 transition-all hover:opacity-90 active:scale-95"
            style={{ backgroundColor: "var(--pitch-green)" }}
          >
            <Sparkles className="w-4 h-4" />
            <span>{t.demoBtn}</span>
          </button>

          {/* Google OAuth Button */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            className="w-full py-2.5 px-4 rounded-xl font-semibold text-xs sm:text-sm border shadow-xs flex items-center justify-center gap-2.5 transition-colors hover:bg-black/5 dark:hover:bg-white/5"
            style={{
              borderColor: "var(--border-color)",
              backgroundColor: "var(--bg-surface)",
              color: "var(--text-main)",
            }}
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
              />
            </svg>
            <span>{t.google}</span>
          </button>

          {/* Divider */}
          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t" style={{ borderColor: "var(--border-color)" }}></div>
            <span className="flex-shrink mx-3 text-[11px] opacity-60" style={{ color: "var(--text-muted)" }}>
              {t.or}
            </span>
            <div className="flex-grow border-t" style={{ borderColor: "var(--border-color)" }}></div>
          </div>

          {/* Email/Password form */}
          <form onSubmit={handleSubmit} className="space-y-2.5">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t.emailPlaceholder}
              className="w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-transparent focus:outline-none transition-colors"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
              }}
            />
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={t.passwordPlaceholder}
              className="w-full px-3.5 py-2.5 rounded-xl border text-xs sm:text-sm bg-transparent focus:outline-none transition-colors"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
              }}
            />

            <button
              type="submit"
              className="w-full py-2.5 rounded-xl font-bold text-xs sm:text-sm border shadow-xs flex items-center justify-center gap-1.5 transition-all hover:bg-black/5 dark:hover:bg-white/5"
              style={{
                borderColor: "var(--border-color)",
                color: "var(--text-main)",
              }}
            >
              <span>{mode === "signup" ? t.signUpBtn : t.signInBtn}</span>
              <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </button>
          </form>

          {/* Mode Switcher */}
          <div className="text-center pt-2 text-xs" style={{ color: "var(--text-muted)" }}>
            {mode === "signup" ? (
              <span>
                {t.haveAccount}{" "}
                <button
                  type="button"
                  onClick={() => setMode("login")}
                  className="font-bold underline text-emerald-600 hover:text-emerald-700"
                >
                  {t.switchSignIn}
                </button>
              </span>
            ) : (
              <span>
                {t.noAccount}{" "}
                <button
                  type="button"
                  onClick={() => setMode("signup")}
                  className="font-bold underline text-emerald-600 hover:text-emerald-700"
                >
                  {t.switchSignUp}
                </button>
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
