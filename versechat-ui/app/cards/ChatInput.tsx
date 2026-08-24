
type ChatInputProps = {
  value: string;
  handleMessage: (value: string) => void;
  handleSend: () => void;
}

const ChatInput = (
  { value, handleMessage, handleSend }: ChatInputProps,
) => {
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key == 'Enter') {
      handleSend()
    }
  }
  return (
    <div className="max-w-5xl w-full h-14 p-2 flex flex-row gap-2 border border-white rounded-3xl">
      <input
        value={value}
        type="text"
        autoComplete="off"
        placeholder="Ask something..."
        className="flex-1 p-4 focus:outline-none focus:ring-0"
        onChange={(e) => handleMessage(e.target.value)}
        onKeyDown={handleKeyDown}
      />

      <button className="py-2 px-6 bg-green-300 rounded-3xl text-black"
        onClick={handleSend}>
        Send
      </button>
    </div>
  );
}
export default ChatInput;
