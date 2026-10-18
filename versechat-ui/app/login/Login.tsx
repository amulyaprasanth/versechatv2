"use client";

import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import type { SubmitEvent } from "react";
import { useState } from "react";

export interface LoginProps {
  onSwitchToRegister: () => void;
  direction?: number;
  onSubmit?: (e: SubmitEvent<HTMLFormElement>) => void;
  onGoogleSignIn?: () => void;
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
  onGoogleSignIn,
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

      {/* Divider */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-px bg-white/20" />
        <span className="text-xs text-white/50">or</span>
        <div className="flex-1 h-px bg-white/20" />
      </div>

      {/* Google */}
      <button
        type="button"
        onClick={onGoogleSignIn}
        className="w-full py-3 rounded-xl bg-white/10 border border-white/25 text-white text-sm font-medium flex items-center justify-center gap-2 hover:bg-white/20 active:scale-95 transition-all duration-150"
      >
        <svg
          className="w-4 h-4"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            fill="#4285F4"
          />
          <path
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            fill="#34A853"
          />
          <path
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"
            fill="#FBBC05"
          />
          <path
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            fill="#EA4335"
          />
        </svg>
        Continue with Google
      </button>

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

