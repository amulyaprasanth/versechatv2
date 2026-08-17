import { Open_Sans } from "next/font/google";

import ChatInput from "../cards/ChatInput";
const opensans = Open_Sans({
  subsets: ["latin"],
});
const ChatContainer = () => {
  const messages: Message[] = [];

  const isEmpty = messages.length === 0;

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
              <ChatInput />
            </div>
          </div>
        ) : (
          /* Chat state */
          <>
            <div className="flex-1 min-h-0 overflow-y-auto">
              {messages.map((message, index) => (
                <div key={index}>{message.content}</div>
              ))}
            </div>

            <div className="shrink-0 flex justify-center">
              <ChatInput />
            </div>
          </>
        )}
      </div>
    </section>
  );
};

export default ChatContainer;
