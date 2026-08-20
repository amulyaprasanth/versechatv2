"use client";

import { Open_Sans } from "next/font/google";
import { useState } from "react";
import ChatInput from "../cards/ChatInput";
import { Message } from "../types/chat";
import MessageCard from "../cards/MessageCard";
import { sendMessage } from "../api/chat";


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

    const userMessage: Message = {
      role: "user",
      content: query,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    try {
      const response = await sendMessage(query);


      setMessages((prev) => [...prev, response]);
      setIsLoading(false);
    } catch {


      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
          error: true,
        },
      ]);
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
              <ChatInput handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            <div className="flex-1 min-h-0 overflow-y-auto">
              <div className="mx-auto flex max-w-3xl flex-col gap-4">
                {messages.map((message, index) => (
                  <MessageCard key={index} message={message} isLoading={isLoading} />
                ))}

              </div>

            </div>
            <div className="shrink-0 flex justify-center">
              <ChatInput handleMessage={onMessage} handleSend={handleSend} />
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default ChatContainer;
