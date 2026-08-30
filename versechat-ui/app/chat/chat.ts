export type Source = {
  tool_name: string;
  tool_output: string;
};

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  error?: boolean;
};

export type ChatResponse = {
  id: string;
  role: "assistant"
  content: string;
  sources: Source[];
};
