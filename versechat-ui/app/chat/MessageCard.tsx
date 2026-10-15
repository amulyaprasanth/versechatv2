
import { Message } from "../chat/chat";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageCard = ({ role, content }: Message) => {
  return (
    <div
      className={`max-w-3xl px-4 py-3 rounded-2xl backdrop-blur-md border shadow-lg text-white
        ${role === "assistant"
          ? "self-start bg-white/15 border-white/30 rounded-tl-none"
          : "self-end bg-white/30 border-white/50 rounded-tr-none"
        }`}
    >
      <ReactMarkdown remarkPlugins={[remarkGfm]}>
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default MessageCard;
