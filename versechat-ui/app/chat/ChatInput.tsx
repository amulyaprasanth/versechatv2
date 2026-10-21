import React from 'react';

type ChatInputProps = {
  value: string;
  handleMessage: (value: string) => void;
  handleSend: () => void;
  disabled?: boolean;
};

const ChatInput = ({
  value,
  handleMessage,
  handleSend,
  disabled = false,
}: ChatInputProps) => {
  const onSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!disabled && value.trim()) {
      handleSend();
    }
  };



  return (
    <form
      onSubmit={onSubmit}
      className="max-w-3xl w-full h-14 p-2 flex flex-row gap-2
                 rounded-3xl
                 bg-white/20 backdrop-blur-md
                 border border-white/50 shadow-xl"
    >
      <input
        value={value}
        type="text"
        autoComplete="off"
        aria-label="Message"
        placeholder="Ask something..."
        className="flex-1 px-4 bg-transparent text-white placeholder-white/70
                   focus:outline-none focus:ring-0 text-base"
        onChange={(event) => handleMessage(event.target.value)}
      />

      <button
        type="submit"
        className="py-2 px-6
                   bg-white text-gray-900 font-semibold
                   hover:bg-white/90 active:scale-95
                   rounded-3xl shadow
                   transition-all duration-150"
      >
        Send
      </button>
    </form>
  );
};

export default ChatInput;
