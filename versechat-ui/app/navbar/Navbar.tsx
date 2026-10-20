"use client";

import { Raleway } from "next/font/google";
import { motion } from "motion/react";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

type UserProfile = {
  fullname: string;
  email: string;
};

const raleway = Raleway({
  subsets: ["latin"],
});

export const Navbar = () => {
  const router = useRouter();
  const [signingOut, setSigningOut] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [profileOpen, setProfileOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;

    fetch("/api/auth/me", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) return null;
        return (await response.json()) as UserProfile;
      })
      .then((user) => {
        if (!cancelled && user) setProfile(user);
      })
      .catch(() => {
        // The avatar remains available with a fallback initial if profile loading fails.
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!profileOpen) return;

    function handlePointerDown(event: PointerEvent) {
      if (
        event.target instanceof Node &&
        !profileMenuRef.current?.contains(event.target)
      ) {
        setProfileOpen(false);
      }
    }

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") setProfileOpen(false);
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [profileOpen]);

  async function handleSignOut() {
    setSigningOut(true);
    try {
      await fetch("/api/auth/logout", { method: "POST" });
    } catch {
      // The logout route clears the cookies locally even if the backend is down.
    } finally {
      router.replace("/login");
      router.refresh();
      setSigningOut(false);
    }
  }

  return (
    <div className="sticky bg-transparent h-16 flex justify-center shadow-l shadow-white">
      <motion.h1
        initial={{ y: -5, scale: 0.5 }}
        animate={{ y: 0, scale: 1 }}
        transition={{ duration: 0.3 }}
        viewport={{ once: true }}
        className={`${raleway.className} text-center text-4xl py-2`}>
        Versechat
      </motion.h1>
      <motion.p
        initial={{ y: -5, scale: 0.5, opacity: 0 }}
        animate={{ y: 0, scale: 1, opacity: 1 }}
        transition={{ duration: 0.3, delay: 0.3 }}
        viewport={{ once: true }}
        className="mb-auto rounded-xl text-white p-1">
        1.0.0
      </motion.p>
      <div ref={profileMenuRef} className="absolute right-4 top-1/2 -translate-y-1/2">
        <button
          type="button"
          onClick={() => setProfileOpen((open) => !open)}
          aria-label="Open profile menu"
          aria-haspopup="menu"
          aria-expanded={profileOpen}
          className="flex h-10 w-10 items-center justify-center rounded-full border border-white/40 bg-white/10 text-lg font-semibold text-white transition hover:bg-white/20 focus:outline-none focus:ring-2 focus:ring-white/70"
        >
          {profile?.fullname.trim().charAt(0).toUpperCase() || "?"}
        </button>
        {profileOpen && (
          <div
            role="menu"
            aria-label="Profile menu"
            className="absolute right-0 top-12 z-50 w-72 rounded-2xl border border-white/15 bg-slate-950/95 p-4 text-left text-white shadow-2xl backdrop-blur-xl"
          >
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-white/50">
              Signed in as
            </p>
            {profile ? (
              <div className="mt-2 min-w-0">
                <p className="truncate font-semibold">{profile.fullname}</p>
                <p className="mt-1 break-all text-sm text-white/65">{profile.email}</p>
              </div>
            ) : (
              <p className="mt-2 text-sm text-white/65">Loading profile…</p>
            )}
            <div className="my-4 border-t border-white/10" />
            <button
              type="button"
              role="menuitem"
              onClick={handleSignOut}
              disabled={signingOut}
              className="w-full rounded-xl bg-white/10 px-3 py-2 text-left text-sm font-medium transition hover:bg-white/15 disabled:cursor-wait disabled:opacity-60"
            >
              {signingOut ? "Signing out…" : "Sign out"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Navbar;
