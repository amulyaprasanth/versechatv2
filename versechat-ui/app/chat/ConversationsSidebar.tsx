"use client";

import React, { useState } from "react";
import { ConversationItem } from "./chat";

interface ConversationsSidebarProps {
  conversations: ConversationItem[];
  activeId: string;
  isLoading: boolean;
  isDeletingId: string | null;
  onSelectConversation: (id: string) => void;
  onNewChat: () => void;
  onDeleteConversation: (id: string) => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

function formatRelativeTime(dateString?: string | null): string {
  if (!dateString) return "";
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return "";
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diffSec < 60) return "Just now";
    const diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return `${diffHour}h ago`;
    const diffDay = Math.floor(diffHour / 24);
    if (diffDay < 7) return `${diffDay}d ago`;
    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

export const ConversationsSidebar: React.FC<ConversationsSidebarProps> = ({
  conversations,
  activeId,
  isLoading,
  isDeletingId,
  onSelectConversation,
  onNewChat,
  onDeleteConversation,
  isOpenMobile,
  onCloseMobile,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null);

  const filteredConversations = conversations.filter((c) =>
    (c.title || "New conversation")
      .toLowerCase()
      .includes(searchQuery.toLowerCase().trim())
  );

  const handleConfirmDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmDeleteId(null);
    onDeleteConversation(id);
  };

  const handleStartDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmDeleteId(id);
  };

  const handleCancelDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    setConfirmDeleteId(null);
  };

  const sidebarContent = (
    <aside
      className="flex flex-col h-full w-full bg-slate-950/70 md:bg-black/40 backdrop-blur-2xl border-r border-white/10 text-white select-none overflow-hidden"
      onClick={() => {
        if (confirmDeleteId) setConfirmDeleteId(null);
      }}
    >
      {/* Sidebar Header & New Chat button */}
      <div className="p-4 pb-3 flex flex-col gap-3 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              className="w-5 h-5 text-sky-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
              />
            </svg>
            <h2 className="font-semibold text-base text-white/90 tracking-wide">
              Conversations
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs px-2 py-0.5 rounded-full bg-white/10 text-white/60 font-mono">
              {conversations.length}
            </span>

            {/* Mobile close button */}
            <button
              type="button"
              onClick={onCloseMobile}
              className="md:hidden p-1.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition"
              aria-label="Close conversation menu"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          type="button"
          onClick={onNewChat}
          className="group relative flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-xl font-medium text-sm text-white bg-gradient-to-r from-sky-500/25 via-indigo-500/25 to-purple-500/25 hover:from-sky-500/35 hover:via-indigo-500/35 hover:to-purple-500/35 border border-white/20 hover:border-white/40 shadow-lg hover:shadow-sky-500/10 active:scale-[0.98] transition-all duration-200"
        >
          <svg
            className="w-4 h-4 text-sky-300 group-hover:rotate-90 transition-transform duration-200"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
          </svg>
          <span>New Chat</span>
        </button>

        {/* Search input (visible if more than 3 conversations) */}
        {conversations.length > 3 && (
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="w-full bg-white/5 border border-white/10 rounded-lg py-1.5 pl-8 pr-3 text-xs text-white placeholder-white/40 focus:outline-none focus:border-white/30 focus:bg-white/10 transition"
            />
            <svg
              className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-white/40"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery("")}
                className="absolute right-2 top-2 text-white/40 hover:text-white text-xs"
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin scrollbar-thumb-white/10">
        {isLoading && conversations.length === 0 ? (
          /* Loading skeleton */
          <div className="space-y-2 p-2">
            {[1, 2, 3, 4].map((i) => (
              <div
                key={i}
                className="h-12 rounded-xl bg-white/5 border border-white/5 animate-pulse"
              />
            ))}
          </div>
        ) : filteredConversations.length === 0 ? (
          /* Empty state */
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center">
            <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                />
              </svg>
            </div>
            <p className="text-sm font-medium text-white/70">
              {searchQuery ? "No matching chats" : "No conversations yet"}
            </p>
            <p className="text-xs text-white/40 mt-1">
              {searchQuery
                ? "Try a different search keyword."
                : "Start a new conversation to ask questions about Scripture."}
            </p>
            {!searchQuery && (
              <button
                type="button"
                onClick={onNewChat}
                className="mt-4 px-3 py-1.5 text-xs rounded-lg bg-white/10 hover:bg-white/20 text-white transition border border-white/10"
              >
                + Start your first chat
              </button>
            )}
          </div>
        ) : (
          filteredConversations.map((item) => {
            const isActive = item.id === activeId;
            const isDeleting = isDeletingId === item.id;
            const isConfirming = confirmDeleteId === item.id;
            const timeAgo = formatRelativeTime(item.updated_at || item.created_at);

            return (
              <div
                key={item.id}
                role="button"
                tabIndex={0}
                onClick={() => onSelectConversation(item.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    onSelectConversation(item.id);
                  }
                }}
                className={`group relative flex items-center justify-between gap-2 px-3 py-2.5 rounded-xl text-left transition-all duration-150 cursor-pointer ${
                  isActive
                    ? "bg-white/15 border border-white/25 text-white shadow-md shadow-black/20"
                    : "text-white/70 hover:text-white hover:bg-white/10 border border-transparent"
                } ${isDeleting ? "opacity-50 pointer-events-none" : ""}`}
              >
                {/* Left side: Icon + Title + Timestamp */}
                <div className="flex items-start gap-2.5 min-w-0 flex-1">
                  <div className="mt-0.5 shrink-0 text-white/50 group-hover:text-sky-300 transition-colors">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={1.75}
                        d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
                      />
                    </svg>
                  </div>

                  <div className="min-w-0 flex-1">
                    <p
                      className={`text-sm truncate font-medium ${
                        isActive ? "text-white" : "text-white/80"
                      }`}
                      title={item.title || "New conversation"}
                    >
                      {item.title || "New conversation"}
                    </p>
                    {timeAgo && (
                      <p className="text-[11px] text-white/40 truncate">
                        {timeAgo}
                      </p>
                    )}
                  </div>
                </div>

                {/* Right side: Delete button / Inline confirm */}
                <div className="shrink-0 flex items-center">
                  {isDeleting ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : isConfirming ? (
                    <div className="flex items-center gap-1 bg-red-950/80 border border-red-500/50 rounded-lg px-2 py-1 shadow-lg">
                      <button
                        type="button"
                        onClick={(e) => handleConfirmDelete(item.id, e)}
                        className="text-xs font-semibold text-red-200 hover:text-white transition"
                        title="Confirm delete"
                      >
                        Delete
                      </button>
                      <button
                        type="button"
                        onClick={handleCancelDelete}
                        className="text-xs text-white/60 hover:text-white ml-1"
                        title="Cancel"
                      >
                        ✕
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={(e) => handleStartDelete(item.id, e)}
                      aria-label={`Delete conversation ${item.title || ""}`}
                      className="opacity-0 group-hover:opacity-100 focus:opacity-100 p-1.5 rounded-lg text-white/40 hover:text-red-400 hover:bg-red-500/20 active:scale-95 transition-all duration-150"
                      title="Delete conversation"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={1.75}
                          d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                        />
                      </svg>
                    </button>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* Footer subtle brand info */}
      <div className="p-3 border-t border-white/10 text-center text-xs text-white/40">
        VerseChat Scripture AI
      </div>
    </aside>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <div className="hidden md:flex md:w-72 lg:w-80 h-full shrink-0 z-20">
        {sidebarContent}
      </div>

      {/* Mobile Drawer */}
      {isOpenMobile && (
        <div className="fixed inset-0 z-50 md:hidden flex">
          {/* Backdrop overlay */}
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={onCloseMobile}
            aria-hidden="true"
          />

          {/* Drawer content */}
          <div className="relative w-4/5 max-w-xs h-full z-10 shadow-2xl">
            {sidebarContent}
          </div>
        </div>
      )}
    </>
  );
};

export default ConversationsSidebar;
