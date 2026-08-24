"use client";


import { Open_Sans } from "next/font/google";
import { useState } from "react";
import ChatInput from "../cards/ChatInput";
import { Message } from "../types/chat";
import MessageCard from "../cards/MessageCard";
import { sendMessage } from "../api/chat";
import MessageLoader from "../cards/MessageLoading";

const opensans = Open_Sans({
  subsets: ["latin"],
});

const ChatContainer = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const isEmpty = messages.length === 0;

  const onMessage = (message: string) => {
    setInputMessage(message);
  };

  const handleSend = async () => {

    if (!inputMessage.trim()) return;

    const query = inputMessage;
    setInputMessage("");

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);

    setIsLoading(true);
    try {
      const response = await sendMessage(query);


      setMessages((prev) => [...prev, response]);
    } catch (error) {
      console.error("Failed to send message:", error);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: "Something went wrong. Please try again.",
          error: true,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="chat-container" className="h-full">
      <div className="mx-auto h-full p-4 bg-slate-600 flex flex-col">
        {isEmpty ? (
          /* Empty state */
          <div className="flex-1 flex items-center justify-center">
            <div className="w-full max-w-3xl flex flex-col gap-2">
              <h1 className={` ${opensans.className} text-center text-3xl`}>
                Hi, Welcome to Versechat!
              </h1>
              <ChatInput value={inputMessage} handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            <div className="flex-1 min-h-0 overflow-y-auto">
              <div className="mx-auto flex max-w-3xl flex-col gap-4">
                {messages.map((message) => (
                  <MessageCard key={message.id} {...message} />
                ))}
                {
                  isLoading && (<div className="w-4 h-2 self-start"> <MessageLoader /></div>)
                }
              </div>

            </div>
            <div className="shrink-0 flex justify-center">
              <ChatInput value={inputMessage} handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default ChatContainer;
