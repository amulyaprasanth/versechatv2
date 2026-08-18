export type Source = {
  tool_name: string;
  tool_output: string;
};

export type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  error?: boolean;
};

export type ChatResponse = {
  role: "assistant"
  content: string;
  sources: Source[];
};