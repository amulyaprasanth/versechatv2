import type { SubmitEvent } from 'react';
type ChatInputProps = {
  value: string;
  handleMessage: (value: string) => void;
  handleSend: () => void;
};

const ChatInput = ({
  value,
  handleMessage,
  handleSend,
}: ChatInputProps) => {
  const onSubmit = (event: SubmitEvent) => {
    event.preventDefault();
    handleSend();
  };


  return (
    <form
      onSubmit={onSubmit}
      className="max-w-5xl w-full h-14 p-2 flex flex-row gap-2 border border-white rounded-3xl"
    >
      <input
        value={value}
        type="text"
        autoComplete="off"
        aria-label="Message"
        placeholder="Ask something..."
        className="flex-1 p-4 focus:outline-none focus:ring-0"
        onChange={(event) => handleMessage(event.target.value)}
      />

      <button
        type="submit"
        className="py-2 px-6 bg-green-300 rounded-3xl text-black"
      >
        Send
      </button>
    </form>
  );
};

export default ChatInput;
