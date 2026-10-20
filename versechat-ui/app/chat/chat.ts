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
  role: "assistant";
  content: string;
  sources: Source[];
};

export type ConversationItem = {
  id: string;
  title: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export type ConversationDetail = {
  id: string;
  title: string;
  messages: Array<{
    role: "user" | "assistant";
    content: string;
  }>;
};

