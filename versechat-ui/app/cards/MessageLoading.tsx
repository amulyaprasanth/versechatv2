const MessageLoader = () => {
  return (
    <div id="loader" className="flex gap-1 justify-center items-center" >
      <div id="dot" className="w-[12px] h-[12px] bg-blue-300 rounded-xl animate-bounce "></div>
      <div id="dot" className="w-[12px] h-[12px] bg-blue-300 rounded-xl animate-bounce [animation-delay: 0.15s]"></div>
      <div id="dot" className="w-[12px] h-[12px] bg-blue-300 rounded-xl animate-bounce [animation-delay:0.3s]"></div>
    </div>
  )
}
export default MessageLoader
