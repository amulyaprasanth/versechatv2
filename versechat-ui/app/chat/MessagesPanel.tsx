"use client";

import React, { useEffect, useRef } from "react";
import { Message } from "./chat";
import MessageCard from "./MessageCard";
import MessageLoader from "./MessageLoading";
import ChatInput from "./ChatInput";
import { Open_Sans } from "next/font/google";

const opensans = Open_Sans({
  subsets: ["latin"],
});

interface MessagesPanelProps {
  messages: Message[];
  inputMessage: string;
  activeTitle?: string;
  isLoading: boolean;
  isFetchingMessages: boolean;
  onInputChange: (message: string) => void;
  onSend: () => void;
  onOpenMobileSidebar: () => void;
}

const STARTER_PROMPTS = [
  {
    title: "Peace in Times of Worry",
    prompt: "What biblical passages offer the best comfort and guidance for anxiety?",
    icon: "🕊️",
  },
  {
    title: "The Prodigal Son",
    prompt: "Explain the historical context and theological depth of the Prodigal Son parable.",
    icon: "📖",
  },
  {
    title: "Understanding Grace",
    prompt: "How does the Bible define grace, and how does it relate to faith and works?",
    icon: "✝️",
  },
  {
    title: "Daily Reflection",
    prompt: "Provide an inspiring scripture verse, a brief reflection, and a prayer for strength today.",
    icon: "🌱",
  },
];

export const MessagesPanel: React.FC<MessagesPanelProps> = ({
  messages,
  inputMessage,
  activeTitle,
  isLoading,
  isFetchingMessages,
  onInputChange,
  onSend,
  onOpenMobileSidebar,
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const isEmpty = messages.length === 0;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <main className="flex-1 flex flex-col h-full min-w-0 relative z-10 overflow-hidden">
      {/* Top Bar / Header */}
      <div className="shrink-0 h-14 px-4 flex items-center justify-between border-b border-white/10 bg-black/20 backdrop-blur-md">
        <div className="flex items-center gap-3 min-w-0">
          {/* Mobile hamburger button */}
          <button
            type="button"
            onClick={onOpenMobileSidebar}
            aria-label="Open conversation list"
            className="md:hidden p-2 rounded-xl text-white/70 hover:text-white hover:bg-white/10 transition active:scale-95"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          {/* Active conversation title */}
          <div className="min-w-0">
            <h1 className="text-sm font-medium text-white truncate max-w-xs sm:max-w-md md:max-w-lg">
              {activeTitle || "New Conversation"}
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="hidden sm:inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-white/10 text-white/70 border border-white/10">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            Online
          </span>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 min-h-0 flex flex-col overflow-hidden relative">
        {isFetchingMessages ? (
          /* Loading messages skeleton */
          <div className="flex-1 flex items-center justify-center">
            <div className="flex items-center gap-3 px-5 py-3 rounded-2xl bg-white/10 border border-white/20 backdrop-blur-md text-white/80 text-sm shadow-xl">
              <div className="w-4 h-4 border-2 border-sky-400 border-t-transparent rounded-full animate-spin" />
              <span>Loading messages...</span>
            </div>
          </div>
        ) : isEmpty ? (
          /* Welcome state */
          <div className="flex-1 overflow-y-auto px-4 py-8 flex items-center justify-center">
            <div className="w-full max-w-3xl flex flex-col items-center gap-6 text-center my-auto">
              <div className="space-y-3">
                <div className="inline-flex p-3 rounded-2xl bg-white/10 border border-white/20 shadow-2xl backdrop-blur-md mb-1">
                  <span className="text-3xl">✨</span>
                </div>
                <h2 className={`${opensans.className} text-3xl sm:text-4xl font-semibold text-white drop-shadow-lg`}>
                  Hi, Welcome to Versechat!
                </h2>
                <p className="text-white/70 text-sm sm:text-base max-w-xl mx-auto">
                  Explore biblical wisdom, ask questions about theology, or seek daily encouragement through Scripture.
                </p>
              </div>

              {/* Starter prompts grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left pt-2">
                {STARTER_PROMPTS.map((item, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => onInputChange(item.prompt)}
                    className="p-3.5 rounded-2xl bg-white/10 hover:bg-white/20 border border-white/15 hover:border-white/30 text-white backdrop-blur-md shadow-lg transition-all duration-200 text-left group active:scale-[0.98]"
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{item.icon}</span>
                      <h3 className="font-medium text-sm text-white/90 group-hover:text-white">
                        {item.title}
                      </h3>
                    </div>
                    <p className="text-xs text-white/60 line-clamp-2">
                      {item.prompt}
                    </p>
                  </button>
                ))}
              </div>

              {/* Initial chat input for empty state */}
              <div className="w-full pt-2">
                <ChatInput
                  value={inputMessage}
                  handleMessage={onInputChange}
                  handleSend={onSend}
                />
              </div>
            </div>
          </div>
        ) : (
          /* Chat conversation message stream */
          <>
            <div className="flex-1 min-h-0 overflow-y-auto px-4 py-6">
              <div className="mx-auto flex max-w-3xl flex-col gap-4 pb-4">
                {messages.map((message) => (
                  <MessageCard key={message.id} {...message} />
                ))}

                {isLoading && (
                  <div className="self-start flex items-center gap-3 rounded-2xl rounded-tl-none border border-white/25 bg-white/15 px-4 py-3 text-sm text-white/80 shadow-lg backdrop-blur-md">
                    <span>VerseChat is thinking</span>
                    <MessageLoader />
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Bottom floating input container */}
            <div className="shrink-0 flex justify-center px-4 py-4 bg-gradient-to-t from-black/60 via-black/30 to-transparent">
              <ChatInput
                value={inputMessage}
                handleMessage={onInputChange}
                handleSend={onSend}
              />
            </div>
          </>
        )}
      </div>
    </main>
  );
};

export default MessagesPanel;
