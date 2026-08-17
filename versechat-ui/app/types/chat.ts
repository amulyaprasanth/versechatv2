type Source = {
  tool_name: string;
  tool_output: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type ChatResponse = {
  role: "assistant"
  content: string;
  sources: Source[];
};