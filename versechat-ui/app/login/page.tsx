"use client";

import Image from "next/image";
import { Open_Sans } from "next/font/google";
import { AnimatePresence } from "motion/react";
import { useState } from "react";
import LoginBg from "@/public/images/login-desktop.webp";
import LoginBgMobile from "@/public/images/login-mobile.webp";
import Login from "./Login";
import Register from "./Register";

const opensans = Open_Sans({ subsets: ["latin"] });

type View = "login" | "signup";

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
              <Login
                key="login"
                direction={direction}
                onSwitchToRegister={() => switchTo("signup")}
              />
            ) : (
              <Register
                key="signup"
                direction={direction}
                onSwitchToLogin={() => switchTo("login")}
              />
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};

export default LoginPage;
