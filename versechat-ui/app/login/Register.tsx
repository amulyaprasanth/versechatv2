"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import type { SubmitEvent } from "react";

export interface RegisterProps {
  onSwitchToLogin: () => void;
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

export const Register = ({
  onSwitchToLogin,
  direction = 1,
  onSubmit,
}: RegisterProps) => {
  const router = useRouter();
  const [fullname, setFullname] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (onSubmit) {
      onSubmit(e);
      return;
    }

    if (!fullname.trim() || !email.trim() || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    setError("");
    setIsLoading(true);

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          fullname: fullname.trim(),
          email: email.trim(),
          password: password,
        }),
      });

      const data = await response.json();
      if (!response.ok) {
        setError(data.detail ?? "Registration failed");
        return;
      }

      // Auto login to set up session/token if possible
      try {
        await fetch("/api/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({
            username: email.trim(),
            password: password,
          }),
        });
      } catch {
        // Proceed even if auto-login token fetch fails
      }

      router.push("/chat");
    } catch {
      setError("Unable to Register. Please try again.");
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
          Create account
        </h1>
        <p className="mt-1 text-sm text-white/70">
          Join VerseChat today
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Fields */}
        <div className="flex flex-col gap-4">
          <input
            type="text"
            value={fullname}
            placeholder="Full name"
            autoComplete="name"
            className={inputClass}
            onChange={(e) => setFullname(e.target.value)}
          />
          <input
            type="email"
            value={email}
            placeholder="Email"
            autoComplete="email"
            className={inputClass}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type="password"
            value={password}
            placeholder="Password"
            autoComplete="new-password"
            className={inputClass}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type="password"
            value={confirmPassword}
            placeholder="Confirm password"
            autoComplete="new-password"
            className={inputClass}
            onChange={(e) => setConfirmPassword(e.target.value)}
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
          disabled={isLoading}
          className="w-full py-3 rounded-xl bg-white text-gray-900 font-semibold text-sm hover:bg-white/90 active:scale-95 transition-all duration-150 shadow disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {isLoading ? "Signing up..." : "Sign Up"}
        </button>
      </form>

      {/* Switch back to login */}
      <p className="text-center text-xs text-white/50">
        Already have an account?{" "}
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-white/80 underline underline-offset-2 hover:text-white"
        >
          Sign in
        </button>
      </p>
    </motion.div>
  );
};

export { Register as RegisterForm };
export default Register;

