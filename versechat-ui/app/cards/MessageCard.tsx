
import { Message } from "../types/chat";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import MessageLoader from "./MessageLoading";


type MessageCardProps = {
  message: Message;
  isLoading: boolean;
}

const MessageCard = ({ message, isLoading }: MessageCardProps) => {
  return (
    <div
      className={`max-w-3xl p-2 rounded-2xl ${message.role === "assistant" ? "self-start text-white text-l/5" : "self-end bg-stone-100 text-black rounded-br-none"}`}>
      {
        isLoading && (message.role == "assistant") ? (<div className="w-4 h-4 self-start"> <MessageLoader /></div>)
          :
          < ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message.content}
          </ReactMarkdown>

      }

    </div >
  );
};

export default MessageCard; 
