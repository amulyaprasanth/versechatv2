"use client";

import { Open_Sans } from "next/font/google";
import { useState } from "react";
import ChatInput from "./ChatInput";
import { Message } from "./chat";
import MessageCard from "./MessageCard";
import MessageLoader from "./MessageLoading";
import Image from "next/image";
import chatBg from "@/public/images/chat-bg.webp";
import chatBgMobile from "@/public/images/chat-bg-mobile.webp";

const opensans = Open_Sans({
  subsets: ["latin"],
});

const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const isEmpty = messages.length === 0;
  const [convId, setConvId] = useState<string>("")
  const onMessage = (message: string) => {
    setInputMessage(message);
  };

  if (messages.length == 0 && convId == "") {
    setConvId(crypto.randomUUID());
  }


  const handleSend = async () => {
    if (!inputMessage.trim()) return;

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
      const response = await fetch('/api/ask/stream', {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          "query": query,
          "conv_id": convId
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
    } catch (error) {
      const content = error instanceof Error && error.message !== "Failed to fetch"
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
            message.id === assistantId ? errorMessage : message,
          )
          : [...prev, errorMessage];
      });
    } finally {
      setIsLoading(false);
    }
  };
  return (
    <section id="chat-container" className="relative h-full">
      <Image
        src={chatBg}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(min-width: 768px) 100vw, 0px"
        className="hidden object-cover md:block"
      />

      {/* Mobile background */}
      <Image
        src={chatBgMobile}
        alt="Reading Bible"
        fill
        priority
        placeholder="blur"
        sizes="(max-width: 767px) 100vw, 0px"
        className="object-cover md:hidden"
      />
      {/* Darker overlay so elements are readable against the dark bg image */}
      <div className="absolute inset-0 bg-black/50 pointer-events-none" />
      <div className="absolute inset-0 pt-16 flex flex-col">
        {isEmpty ? (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center px-4">
            <div className="w-full max-w-3xl flex flex-col gap-4">
              <h1 className={`${opensans.className} text-center text-4xl font-semibold text-white drop-shadow-lg`}>
                Hi, Welcome to Versechat!
              </h1>
              <ChatInput value={inputMessage} handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            <div className="flex-1 min-h-0 overflow-y-auto px-4 py-4">
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
              </div>
            </div>
            <div className="shrink-0 flex justify-center px-4 py-4
                            bg-gradient-to-t from-black/40 to-transparent">
              <ChatInput value={inputMessage} handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default ChatContainer;
