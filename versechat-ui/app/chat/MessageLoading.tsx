const MessageLoader = () => {
  return (
    <output aria-label="Assistant is thinking" aria-live="polite" className="flex items-center gap-1.5">
      <span aria-hidden="true" className="h-2 w-2 rounded-full bg-sky-200 animate-bounce [animation-delay:-0.3s]" />
      <span aria-hidden="true" className="h-2 w-2 rounded-full bg-sky-200 animate-bounce [animation-delay:-0.15s]" />
      <span aria-hidden="true" className="h-2 w-2 rounded-full bg-sky-200 animate-bounce" />
    </output>
  )
}
export default MessageLoader
