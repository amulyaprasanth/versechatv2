import os

from groq import RateLimitError
from langchain.agents import create_agent
from langchain.messages import ToolMessage
from langchain.tools import BaseTool
from langchain_groq import ChatGroq
from pydantic import SecretStr

from versechat_backend.core.logger import get_logger

logger = get_logger()


class BibleAgent:
    """An intelligent assistant for answering Bible-related and factual questions."""

    def __init__(self, model_name: str, tools: list[BaseTool]):
        self.groq_api_key = os.getenv("GROQ_API_KEY", "")
        self.model_name = model_name
        self.tools = tools

        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model_name is empty")

        if len(tools) == 0:
            raise ValueError("No tools to bind the model. Tools list is empty")

        if not self.groq_api_key.strip():
            raise ValueError("Error: GROQ_API_KEY is missing")

        # Define system prompt
        self.prompt_template = """
        You are a helpful Bible assistant that answers questions about the Bible and related topics.

        Your primary purpose is to help users understand Scripture in a clear, accurate, and accessible way. DO NOT ANSWER IF THE QUESTION IS NOT RELATED TO BIBLE AND CHRISTIANITY
        
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
        3. If you want to use wikipedia tool, craft a page title and then search using that title
        
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

        try:
            self.model = ChatGroq(
                model=self.model_name,
                api_key=SecretStr(self.groq_api_key),
                temperature=0.3,
            )

        except ValueError:
            raise ValueError(
                "Invalid model name. Please check [https://console.groq.com/docs/models](https://console.groq.com/docs/models) for a list of supported models."
            )

        # Create agent
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=self.prompt_template,
        )

    async def ask(self, query: str) -> tuple[str, list[dict]]:
        """Ask the assistant a question with optional prior messages (memory) and get the response."""

        if not isinstance(query, str) or not query.strip():
            raise ValueError("query should not be empty")

        try:
            input_message = {"role": "user", "content": query}
            response = await self.agent.ainvoke({"messages": [input_message]})
            answer = response["messages"][-1].content

            tool_messages = [
                msg for msg in response["messages"] if isinstance(msg, ToolMessage)
            ]

            sources = []

            for msg in tool_messages:
                source = {"tool_name": msg.name, "tool_output": msg.content}
                sources.append(source)

            return answer, sources
        except RateLimitError:
            return "Rate limit reached! Please try after some time", []

        except RuntimeError as e:
            logger.error(f"Agent invocation failed: {e!s}")
            return "Sorry, something went wrong while processing your request.", []


if __name__ == "__main__":  # pragma: no cover
    import asyncio

    from versechat_backend.rag.tools import bible_search, wiki_tool

    assistant = BibleAgent(
        model_name="openai/gpt-oss-20b", tools=[bible_search, wiki_tool]
    )
    query = "what is sin?"
    print("User:", query)

    answer, sources = asyncio.run(assistant.ask(query))
    print(answer)
    print("*" * 36)
    print(sources)
