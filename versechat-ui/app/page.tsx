import Image from "next/image";
import Link from "next/link";
import { Open_Sans } from "next/font/google";
import heroBg from "@/public/images/hero-desktop.jpg";
import heroBgMobile from "@/public/images/hero-mobile.jpg";

const opensans = Open_Sans({ subsets: ["latin"] });

const features = [
  {
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-7 h-7"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.8}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z"
        />
      </svg>
    ),
    title: "Semantic Search",
    desc: "Finds relevant passages by meaning, not just keywords, powered by PostgreSQL and pgvector.",
  },
  {
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-7 h-7"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.8}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 12a9 9 0 1 0 18 0 9 9 0 0 0-18 0zm9-4v4l3 3"
        />
      </svg>
    ),
    title: "Web-Enriched Answers",
    desc: "Pulls in context from Wikipedia and live web search to deepen every response.",
  },
  {
    icon: (
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="w-7 h-7"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.8}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.77 9.77 0 0 1-4-.84L3 20l1.09-3.27A7.93 7.93 0 0 1 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
        />
      </svg>
    ),
    title: "Conversation History",
    desc: "Persistent chat history lets you pick up any discussion right where you left off.",
  },
];

const stack = [
  "PostgreSQL",
  "pgvector",
  "FastAPI",
  "LangChain",
  "React",
  "Google OAuth",
];

export default function Home() {
  return (
    <main className={`${opensans.className} relative h-dvh w-full overflow-hidden`}>
      {/* Desktop background */}
      <Image
        src={heroBg}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(min-width: 768px) 100vw, 0px"
        className="hidden object-cover md:block"
      />

      {/* Mobile background */}
      <Image
        src={heroBgMobile}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(max-width: 767px) 100vw, 0px"
        className="object-cover md:hidden"
      />

      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/65 via-black/35 to-black/60 pointer-events-none" />

      {/* Scrollable content column */}
      <div className="relative h-full overflow-y-auto">
        <div className="min-h-full flex flex-col justify-center items-center
                        px-5 py-16
                        md:px-8 md:py-20">

          {/* ── Hero ── */}
          <div className="text-center mb-12 md:mb-14">
            <h1 className="text-5xl font-bold tracking-tight text-white drop-shadow-lg
                           md:text-7xl">
              VerseChat
            </h1>

            <p className="mt-4 text-base text-white/80 max-w-sm mx-auto leading-relaxed
                          md:text-xl md:max-w-2xl md:mt-5">
              AI-powered Bible assistant delivering contextual, Scripture-based
              answers — enriched with Wikipedia and web search.
            </p>

            {/* CTA */}
            <Link
              href="/chat"
              className="inline-block mt-8 px-9 py-3.5 rounded-full
                         bg-white text-gray-900 font-semibold text-base shadow-lg
                         hover:bg-white/90 active:scale-95 transition-all duration-150
                         md:mt-10 md:px-11 md:py-4 md:text-lg"
            >
              Start Chatting →
            </Link>
          </div>

          {/* ── Feature cards ── */}
          {/* Mobile: vertical stack  |  Desktop: 3-column grid */}
          <div className="grid grid-cols-1 gap-4 w-full max-w-xs
                          sm:grid-cols-3 sm:max-w-3xl sm:gap-6
                          mb-10 md:mb-12">
            {features.map((f) => (
              <div
                key={f.title}
                className="flex flex-col items-center text-center gap-3
                           rounded-2xl bg-white/15 backdrop-blur-md
                           border border-white/25 shadow-md
                           px-6 py-7 text-white
                           md:px-7 md:py-8"
              >
                <div className="p-3 rounded-full bg-white/20">{f.icon}</div>
                <h3 className="font-semibold text-sm tracking-wide md:text-base">
                  {f.title}
                </h3>
                <p className="text-xs text-white/70 leading-relaxed md:text-sm">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>

          {/* ── Tech stack pills ── */}
          <div className="flex flex-wrap justify-center gap-2 max-w-xs sm:max-w-xl">
            {stack.map((tech) => (
              <span
                key={tech}
                className="px-3.5 py-1.5 rounded-full text-xs font-medium
                           bg-white/10 border border-white/20
                           text-white/75 backdrop-blur-sm
                           md:text-sm md:px-4 md:py-2"
              >
                {tech}
              </span>
            ))}
          </div>

        </div>
      </div>
    </main>
  );
}
