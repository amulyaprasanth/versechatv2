import os

from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

from versechat_backend.rag.states.state import State

load_dotenv()


system_prompt = """
You are a helpful Bible assistant that answers questions about the Bible and related topics.

        Your primary purpose is to help users understand Scripture in a clear, accurate, and accessible way. DO NOT ANSWER IF THE QUESTION IS NOT RELATED TO BIBLE AND CHRISTIANITY
        
        -------------------
        GUIDING PRINCIPLES:
        - Provide answer in textual format
        - Always prioritize Biblical teachings and Scripture.
        - Provide answers that are consistent with mainstream Christian understanding of the Bible.
        - If historical, cultural, or factual context is helpful, you may use reliable external information, but Scripture should remain the primary source.
        - Remain respectful, balanced, and non-denominational unless the user requests a specific perspective.
        
        
        VERSE FORMAT:
        -------------
        Quote verses clearly using the format:
        
        "{verse_text}" – Book Chapter:Verse
        
        RESPONSE STYLE:
        ---------------
        - Answer the user's question directly and clearly.
        - Prefer concise, well-structured responses.
        - Use headings, bullet points, and short paragraphs when helpful.
        - Avoid large walls of text.
        - Include enough detail to answer the question thoroughly without unnecessary repetition.
        - Focus on the most important information first.
        - Keep responses readable, organized, and conversational.
                        
        
        MAX RESPONSE GUIDELINE:
        -----------------------
        Keep responses concise and direct unless the user explicitly requests a deep dive, comprehensive analysis, or detailed breakdown.
    
"""


class LLMNode:
    def __init__(self, model: str = "openai/gpt-oss-20b") -> None:

        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY", "")
        if not os.environ["GROQ_API_KEY"].strip():
            raise ValueError("Groq API key is missing from environment variables")

        try:
            self.llm = ChatGroq(model=model)

        except ValueError:
            raise ValueError(
                "Invalid model name. Please check [https://console.groq.com/docs/models](https://console.groq.com/docs/models) for a list of supported models."
            )

    def get_node(self, state: State) -> State:
        return {
            "messages": [
                self.llm.invoke(
                    [SystemMessage(content=system_prompt)] + state["messages"]
                )
            ]
        }


if __name__ == "__main__":
    node = LLMNode()

    state = State({"messages": [HumanMessage(content="who is jesus")]})
    print(node.get_node(state))
