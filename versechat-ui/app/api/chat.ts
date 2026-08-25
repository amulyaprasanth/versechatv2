import axios from "axios";
import { BASE_API_URL } from "./api";
import { Message } from "../types/chat";

export const sendMessage = async (query: string): Promise<Message> => {
  try {
    const response = await axios.post(`${BASE_API_URL}/ask`, {
      query,
    });

    return response.data;
  } catch (error) {
    console.error("Failed to send message:", error);
    throw error;
  }
};
