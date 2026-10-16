"use client";

import Image from "next/image";
import { Open_Sans } from "next/font/google";
import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";
import LoginBg from "@/public/images/login-desktop.webp";
import LoginBgMobile from "@/public/images/login-mobile.webp";

const opensans = Open_Sans({ subsets: ["latin"] });

type View = "login" | "signup";

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

const LoginPage = () => {
  const [view, setView] = useState<View>("login");
  const [direction, setDirection] = useState(1);

  const switchTo = (next: View) => {
    setDirection(next === "signup" ? 1 : -1);
    setView(next);
  };

  return (
    <section
      className={`${opensans.className} relative h-dvh w-full overflow-hidden`}
    >
      {/* Desktop background */}
      <Image
        src={LoginBg}
        alt="Open bible"
        fill
        priority
        placeholder="blur"
        sizes="(min-width: 768px) 100vw, 0px"
        className="hidden object-cover md:block"
      />

      {/* Mobile background */}
      <Image
        src={LoginBgMobile}
        alt="Open bible portrait"
        fill
        priority
        placeholder="blur"
        sizes="(max-width: 767px) 100vw, 0px"
        className="object-cover md:hidden"
      />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/65 via-black/35 to-black/60 pointer-events-none" />

      {/* Card container — clips the sliding panels */}
      <div className="relative h-full flex items-center justify-center px-4">
        <div className="relative w-full max-w-sm overflow-hidden rounded-2xl bg-white/15 backdrop-blur-md border border-white/25 shadow-xl">
          <AnimatePresence mode="wait" custom={direction}>
            {view === "login" ? (
              <motion.div
                key="login"
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

                {/* Fields */}
                <div className="flex flex-col gap-4">
                  <input
                    type="email"
                    placeholder="Email"
                    autoComplete="email"
                    className={inputClass}
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    autoComplete="current-password"
                    className={inputClass}
                  />
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-white text-gray-900 font-semibold text-sm hover:bg-white/90 active:scale-95 transition-all duration-150 shadow"
                >
                  Sign In
                </button>

                {/* Divider */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-px bg-white/20" />
                  <span className="text-xs text-white/50">or</span>
                  <div className="flex-1 h-px bg-white/20" />
                </div>

                {/* Google */}
                <button
                  type="button"
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
                    onClick={() => switchTo("signup")}
                    className="text-white/80 underline underline-offset-2 hover:text-white"
                  >
                    Sign up
                  </button>
                </p>
              </motion.div>
            ) : (
              <motion.div
                key="signup"
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

                {/* Fields */}
                <div className="flex flex-col gap-4">
                  <input
                    type="text"
                    placeholder="Full name"
                    autoComplete="name"
                    className={inputClass}
                  />
                  <input
                    type="email"
                    placeholder="Email"
                    autoComplete="email"
                    className={inputClass}
                  />
                  <input
                    type="password"
                    placeholder="Password"
                    autoComplete="new-password"
                    className={inputClass}
                  />
                  <input
                    type="password"
                    placeholder="Confirm password"
                    autoComplete="new-password"
                    className={inputClass}
                  />
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  className="w-full py-3 rounded-xl bg-white text-gray-900 font-semibold text-sm hover:bg-white/90 active:scale-95 transition-all duration-150 shadow"
                >
                  Sign Up
                </button>

                {/* Divider */}
                <div className="flex items-center gap-3">
                  <div className="flex-1 h-px bg-white/20" />
                  <span className="text-xs text-white/50">or</span>
                  <div className="flex-1 h-px bg-white/20" />
                </div>

                {/* Google */}
                <button
                  type="button"
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

                {/* Switch back to login */}
                <p className="text-center text-xs text-white/50">
                  Already have an account?{" "}
                  <button
                    onClick={() => switchTo("login")}
                    className="text-white/80 underline underline-offset-2 hover:text-white"
                  >
                    Sign in
                  </button>
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default LoginPage;
