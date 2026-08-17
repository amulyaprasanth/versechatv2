const ChatInput = () => (
  <div className="max-w-5xl w-full h-14 p-2 flex flex-row gap-2 border border-white rounded-3xl">
    <input
      type="text"
      placeholder="Ask something..."
      className="flex-1 p-4 focus:outline-none focus:ring-0"
    />

    <button className="py-2 px-6 bg-green-300 rounded-3xl text-black">
      Send
    </button>
  </div>
);

export default ChatInput;