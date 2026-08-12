import os

from langchain.agents import create_agent
from langchain_groq import ChatGroq

from versechat_backend.core.logger import get_logger
from versechat_backend.rag.tools import bible_search

logger = get_logger()


class BibleAssistant:
    """An intelligent assistant for answering Bible-related and factual questions."""

    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")

        # Define system prompt
        self.prompt_template = """
        You are a helpful Bible assistant that answers questions about the Bible and related topics.

        Your primary purpose is to help users understand Scripture in a clear, accurate, and accessible way.
        
        GUIDING PRINCIPLES:
        -------------------
        - Always prioritize Biblical teachings and Scripture.
        - Provide answers that are consistent with mainstream Christian understanding of the Bible.
        - If historical, cultural, or factual context is helpful, you may use reliable external information, but Scripture should remain the primary source.
        - Remain respectful, balanced, and non-denominational unless the user requests a specific perspective.
        
        
        CONSTRAINTS:
        -----------
        1. Use bible_search first whenever the question relates to Scripture, Christian teachings, Biblical characters, theology, or spiritual topics.
        2. Do not rely on external sources when Scripture alone sufficiently answers the question.
        
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

        # Initialize model
        self.model = ChatGroq(model="llama-3.1-8b-instant")
        self.tools = [bible_search]

        # Create agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.prompt_template,
        )

    async def ask(self, query: str, messages: list | None = None) -> str:
        """Ask the assistant a question with optional prior messages (memory) and get the response."""
        try:
            if messages is None:
                messages = []
            input_messages = messages + [{"role": "user", "content": query}]
            response = await self.agent.ainvoke({"messages": input_messages})
            answer = response["messages"][-1].content

            return answer
        except RuntimeError as e:
            logger.error(f"Agent invocation failed: {e!s}")
            return "Sorry, something went wrong while processing your request."


if __name__ == "__main__":
    assistant = BibleAssistant()
    query = "who is jesus christ?"
    print("User:", query)
    result = assistant.ask(query)
    print(result)
