"use client";

import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import type { SubmitEvent } from "react";
import { useState } from "react";

export interface LoginProps {
  onSwitchToRegister: () => void;
  direction?: number;
  onSubmit?: (e: SubmitEvent<HTMLFormElement>) => void;
}

const variants = {
  enter: (direction: number) => ({
    x: direction > 0 ? "100%" : "-100%",
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction: number) => ({
    x: direction > 0 ? "-100%" : "100%",
    opacity: 0,
  }),
};

const inputClass =
  "w-full px-4 py-3 rounded-xl bg-white/10 border border-white/25 text-white placeholder-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-white/30";

export const Login = ({
  onSwitchToRegister,
  direction = 1,
  onSubmit,
}: LoginProps) => {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(e);
      return;
    }

    if (!email.trim() || !password) return;
    setError("");
    setIsLoading(true);

    const body = new URLSearchParams({
      username: email,
      password: password,
    });

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: body,
      });

      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Login failed");
        return;
      }
      router.push("/chat");
    } catch {
      setError("Unable to Login. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      custom={direction}
      variants={variants}
      initial="enter"
      animate="center"
      exit="exit"
      transition={{ duration: 0.35, ease: "easeInOut" }}
      className="px-8 py-10 flex flex-col gap-5"
    >
      {/* Title */}
      <div className="text-center mb-2">
        <h1 className="text-3xl font-bold text-white tracking-tight">
          Welcome back
        </h1>
        <p className="mt-1 text-sm text-white/70">
          Sign in to continue to VerseChat
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Fields */}
        <div className="flex flex-col gap-4">
          <input
            type="email"
            value={email}
            placeholder="Email"
            required
            autoComplete="email"
            className={inputClass}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            value={password}
            placeholder="Password"
            required
            autoComplete="current-password"
            className={inputClass}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        {/* Error */}
        {error && (
          <p role="alert" className="text-sm text-red-400">
            {error}
          </p>
        )}

        {/* Submit */}
        <button
          type="submit"
          className="w-full py-3 rounded-xl bg-white text-gray-900 font-semibold text-sm hover:bg-white/90 active:scale-95 transition-all duration-150 shadow disabled:opacity-80 disabled:cursor-wait inline-flex items-center justify-center gap-2"
          disabled={isLoading}
          aria-busy={isLoading}
        >
          {isLoading ? (
            <>
              <svg
                aria-hidden="true"
                className="h-4 w-4 animate-spin"
                viewBox="0 0 24 24"
                fill="none"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="9"
                  stroke="currentColor"
                  strokeWidth="3"
                />
                <path
                  className="opacity-90"
                  d="M21 12a9 9 0 0 0-9-9"
                  stroke="currentColor"
                  strokeWidth="3"
                  strokeLinecap="round"
                />
              </svg>
              <span>Signing in…</span>
            </>
          ) : (
            "Sign In"
          )}
        </button>
      </form>

      {/* Switch to signup */}
      <p className="text-center text-xs text-white/50">
        Don&apos;t have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToRegister}
          className="text-white/80 underline underline-offset-2 hover:text-white"
        >
          Sign up
        </button>
      </p>
    </motion.div>
  );
};

export { Login as LoginForm };
export default Login;

