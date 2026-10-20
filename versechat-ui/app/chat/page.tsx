"use client";

import { useEffect, useState, useCallback } from "react";
import Image from "next/image";
import chatBg from "@/public/images/chat-bg.webp";
import chatBgMobile from "@/public/images/chat-bg-mobile.webp";
import { ConversationItem, Message } from "./chat";
import ConversationsSidebar from "./ConversationsSidebar";
import MessagesPanel from "./MessagesPanel";

const ChatContainer = () => {
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [convId, setConvId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isFetchingConversations, setIsFetchingConversations] = useState<boolean>(true);
  const [isFetchingMessages, setIsFetchingMessages] = useState<boolean>(false);
  const [isDeletingId, setIsDeletingId] = useState<string | null>(null);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

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

  // Handle sending a message
  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const query = inputMessage;
    setInputMessage("");

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
    };

    setMessages((prev: Message[]) => [...prev, userMessage]);
    setIsLoading(true);

    const assistantId = crypto.randomUUID();
    try {
      let conversationId = convId;
      if (!conversationId) {
        const createResponse = await fetch("/api/conversations", {
          method: "POST",
        });
        const createData: unknown = await createResponse.json().catch(() => null);

        if (!createResponse.ok) {
          const detail =
            createData &&
            typeof createData === "object" &&
            "detail" in createData &&
            typeof createData.detail === "string"
              ? createData.detail
              : "Could not create a conversation. Please try again.";
          throw new Error(detail);
        }

        if (
          !createData ||
          typeof createData !== "object" ||
          !("id" in createData) ||
          typeof createData.id !== "string"
        ) {
          throw new Error("The server returned an invalid conversation.");
        }

        conversationId = createData.id;
        setConvId(conversationId);
        await refreshConversations();
      }

      const response = await fetch("/api/ask/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
          conv_id: conversationId,
        }),
      });

      if (!response.ok) {
        const responseText = await response.text();
        let detail: string | undefined;

        try {
          const errorData: { detail?: unknown } = JSON.parse(responseText);
          if (typeof errorData.detail === "string") {
            detail = errorData.detail;
          }
        } catch {
          // The backend may return a plain-text error body.
        }

        if (response.status === 401) {
          throw new Error("Your session has expired. Please sign in again.");
        }

        throw new Error(detail ?? "Sorry, I couldn't get a response. Please try again.");
      }

      if (!response.body) {
        throw new Error("No response body from server");
      }

      setMessages((prev: Message[]) => [
        ...prev,
        {
          id: assistantId,
          role: "assistant",
          content: "",
        },
      ]);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let isFirstToken = false;
      let done = false;

      while (!done) {
        const { value, done: doneReading } = await reader.read();
        done = doneReading;

        if (value) {
          const chunk = decoder.decode(value, {
            stream: !done,
          });

          if (chunk && !isFirstToken) {
            isFirstToken = true;
            setIsLoading(false);
          }

          setMessages((prev: Message[]) =>
            prev.map((message) =>
              message.id === assistantId
                ? {
                    ...message,
                    content: message.content + chunk,
                  }
                : message
            )
          );
        }
      }

      const remaining = decoder.decode();
      if (remaining) {
        setMessages((prev: Message[]) =>
          prev.map((message) =>
            message.id === assistantId
              ? {
                  ...message,
                  content: message.content + remaining,
                }
              : message
          )
        );
      }

      // Re-fetch conversations list so new title or updated time is displayed in sidebar
      refreshConversations();
    } catch (error) {
      const content =
        error instanceof Error && error.message !== "Failed to fetch"
          ? error.message
          : "Unable to connect right now. Please check your connection and try again.";

      setMessages((prev) => {
        const errorMessage: Message = {
          id: assistantId,
          role: "assistant",
          content,
          error: true,
        };

        return prev.some((message) => message.id === assistantId)
          ? prev.map((message) =>
              message.id === assistantId ? errorMessage : message
            )
          : [...prev, errorMessage];
      });
    } finally {
      setIsLoading(false);
    }
  };

  const activeConversation = conversations.find((c) => c.id === convId);
  const activeTitle = activeConversation
    ? activeConversation.title
    : messages.length > 0
    ? "Conversation"
    : "New Conversation";

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
      <div className="absolute inset-0 pt-16 flex flex-row overflow-hidden">
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
    </section>
  );
};

export default ChatContainer;
