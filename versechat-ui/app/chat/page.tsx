"use client";

import { useEffect, useState, useCallback } from "react";
import Image from "next/image";
import chatBg from "@/public/images/chat-bg.webp";
import chatBgMobile from "@/public/images/chat-bg-mobile.webp";
import { ConversationItem, Message } from "./chat";
import ConversationsSidebar from "./ConversationsSidebar";
import MessagesPanel from "./MessagesPanel";

const ChatContainer = () => {
  const bannerMessage = process.env.NEXT_PUBLIC_CHAT_BANNER_MESSAGE?.trim() ?? "";
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [convId, setConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isFetchingConversations, setIsFetchingConversations] = useState<boolean>(true);
  const [isFetchingMessages, setIsFetchingMessages] = useState<boolean>(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);
  const [isBannerDismissed, setIsBannerDismissed] = useState<boolean>(false);

  // Fetch list of conversations for this user
  const refreshConversations = useCallback(async () => {
    try {
      const res = await fetch("/api/conversations", { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        setConversations(data.conversations || []);
      }
    } catch (err) {
      console.error("Failed to refresh conversations:", err);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    async function loadInitialConversations() {
      try {
        const res = await fetch("/api/conversations", { cache: "no-store" });
        if (res.ok) {
          const data = await res.json();
          if (!ignore) {
            setConversations(data.conversations || []);
          }
        }
      } catch (err) {
        console.error("Failed to fetch conversations:", err);
      } finally {
        if (!ignore) {
          setIsFetchingConversations(false);
        }
      }
    }

    void loadInitialConversations();
    return () => {
      ignore = true;
    };
  }, []);


  // Handle selecting a conversation from the sidebar
  const handleSelectConversation = async (id: string) => {
    if (id === convId && messages.length > 0) {
      setIsMobileSidebarOpen(false);
      return;
    }

    setConvId(id);
    setIsMobileSidebarOpen(false);
    setIsFetchingMessages(true);

    try {
      const res = await fetch(`/api/conversations/${id}`, { cache: "no-store" });
      if (res.ok) {
        const data = await res.json();
        const loadedMessages: Message[] = (data.messages || []).map(
          (m: { role: "user" | "assistant"; content: string }) => ({
            id: crypto.randomUUID(),
            role: m.role,
            content: m.content,
          })
        );
        setMessages(loadedMessages);
      } else {
        setMessages([]);
      }
    } catch (err) {
      console.error("Failed to load conversation messages:", err);
      setMessages([]);
    } finally {
      setIsFetchingMessages(false);
    }
  };

  // Handle creating a new chat
  const handleNewChat = () => {
    setConvId(null);
    setMessages([]);
    setInputMessage("");
    setIsMobileSidebarOpen(false);
  };

  // Handle deleting a conversation
  const handleDeleteConversation = async (id: string) => {
    setIsDeletingId(id);
    try {
      const res = await fetch(`/api/conversations/${id}`, {
        method: "DELETE",
      });

      if (res.ok || res.status === 204) {
        setConversations((prev) => prev.filter((c) => c.id !== id));

        // If the deleted conversation was the active one, switch or create new
        if (convId === id) {
          const remaining = conversations.filter((c) => c.id !== id);
          if (remaining.length > 0) {
            void handleSelectConversation(remaining[0].id);
          } else {
            handleNewChat();
          }
        }
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    } finally {
      setIsDeletingId(null);
    }
  };

  const onMessageChange = (message: string) => {
    setInputMessage(message);
  };

  async function createConversation(): Promise<string> {
    const response = await fetch("/api/conversations", { method: "POST" });
    const data: unknown = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(getResponseDetail(data) ?? "Could not create a conversation. Please try again.");
    }
    if (!data || typeof data !== "object" || !("id" in data) || typeof data.id !== "string") {
      throw new Error("The server returned an invalid conversation.");
    }

    setConvId(data.id);
    await refreshConversations();
    return data.id;
  }

  function getResponseDetail(data: unknown): string | undefined {
    if (!data || typeof data !== "object" || !("detail" in data)) return undefined;
    return typeof data.detail === "string" ? data.detail : undefined;
  }

  async function readErrorResponse(response: Response): Promise<string> {
    const responseText = await response.text();
    try {
      return getResponseDetail(JSON.parse(responseText)) ?? "Sorry, I couldn't get a response. Please try again.";
    } catch {
      return "Sorry, I couldn't get a response. Please try again.";
    }
  }

  async function streamAssistantMessage(response: Response, assistantId: string) {
    if (!response.body) throw new Error("No response body from server");

    setMessages((prev) => [...prev, { id: assistantId, role: "assistant", content: "" }]);
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let hasReceivedToken = false;
    let finished = false;

    while (!finished) {
      const { value, done } = await reader.read();
      finished = done;
      if (!value) continue;

      const chunk = decoder.decode(value, { stream: !finished });
      if (chunk && !hasReceivedToken) {
        hasReceivedToken = true;
        setIsLoading(false);
      }
      appendAssistantChunk(assistantId, chunk);
    }

    appendAssistantChunk(assistantId, decoder.decode());
  }

  function appendAssistantChunk(assistantId: string, chunk: string) {
    if (!chunk) return;
    setMessages((prev) => prev.map((message) =>
      message.id === assistantId
        ? { ...message, content: message.content + chunk }
        : message,
    ));
  }

  function displayAssistantError(assistantId: string, error: unknown) {
    const content = error instanceof Error && error.message !== "Failed to fetch"
      ? error.message
      : "Unable to connect right now. Please check your connection and try again.";
    const errorMessage: Message = {
      id: assistantId,
      role: "assistant",
      content,
      error: true,
    };
    setMessages((prev) => {
      if (!prev.some((message) => message.id === assistantId)) {
        return [...prev, errorMessage];
      }
      return prev.map((message) =>
        message.id === assistantId ? errorMessage : message,
      );
    });
  }

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const query = inputMessage;
    setInputMessage("");
    setMessages((prev) => [...prev, {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
    }]);
    setIsLoading(true);

    const assistantId = crypto.randomUUID();
    try {
      const conversationId = convId ?? await createConversation();
      const response = await fetch("/api/ask/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, conv_id: conversationId }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error("Your session has expired. Please sign in again.");
        }
        throw new Error(await readErrorResponse(response));
      }

      await streamAssistantMessage(response, assistantId);
      void refreshConversations();
    } catch (error) {
      displayAssistantError(assistantId, error);
    } finally {
      setIsLoading(false);
    }
  };

  const activeConversation = conversations.find((c) => c.id === convId);
  let activeTitle = "New Conversation";
  if (activeConversation) {
    activeTitle = activeConversation.title;
  } else if (messages.length > 0) {
    activeTitle = "Conversation";
  }

  return (
    <section id="chat-container" className="relative h-full w-full overflow-hidden">
      {/* Background Images */}
      <Image
        src={chatBg}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(min-width: 768px) 100vw, 0px"
        className="hidden object-cover md:block select-none pointer-events-none"
      />

      <Image
        src={chatBgMobile}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(max-width: 767px) 100vw, 0px"
        className="object-cover md:hidden select-none pointer-events-none"
      />

      {/* Dark overlay */}
      <div className="absolute inset-0 bg-black/55 pointer-events-none" />

      {/* Main Container below navbar */}
      <div className="absolute inset-0 pt-16 flex flex-col overflow-hidden">
        {bannerMessage && !isBannerDismissed && (
          <div
            role="status"
            className="z-10 flex shrink-0 items-center justify-between gap-4 border-b border-amber-300 bg-amber-100 px-4 py-2.5 text-sm text-amber-950 shadow-sm md:px-6"
          >
            <p>{bannerMessage}</p>
            <button
              type="button"
              aria-label="Dismiss notice"
              onClick={() => setIsBannerDismissed(true)}
              className="inline-flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-amber-900 transition hover:bg-amber-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-amber-700"
            >
              <span aria-hidden="true" className="text-lg leading-none">×</span>
            </button>
          </div>
        )}

        <div className="flex min-h-0 flex-1 flex-row overflow-hidden">
          {/* Left Component: Conversations List */}
          <ConversationsSidebar
            conversations={conversations}
            activeId={convId ?? ""}
            isLoading={isFetchingConversations}
            isDeletingId={isDeletingId}
            onSelectConversation={handleSelectConversation}
            onNewChat={handleNewChat}
            onDeleteConversation={handleDeleteConversation}
            isOpenMobile={isMobileSidebarOpen}
            onCloseMobile={() => setIsMobileSidebarOpen(false)}
          />

          {/* Right Component: Messages & Chat Area */}
          <MessagesPanel
            messages={messages}
            inputMessage={inputMessage}
            activeTitle={activeTitle}
            isLoading={isLoading}
            isFetchingMessages={isFetchingMessages}
            onInputChange={onMessageChange}
            onSend={handleSend}
            onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          />
        </div>
      </div>
    </section>
  );
};

export default ChatContainer;
