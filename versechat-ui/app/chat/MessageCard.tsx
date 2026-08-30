
import { Message } from "../chat/chat";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageCard = ({ role, content }: Message) => {
  return (
    <div
      className={`max-w-3xl p-2 rounded-2xl ${role === "assistant" ? "self-start text-white text-l/5" : "self-end bg-stone-100 text-black rounded-br-none"}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MessageCard; 
