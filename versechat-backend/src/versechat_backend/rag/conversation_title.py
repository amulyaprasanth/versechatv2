import re

from langchain.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from versechat_backend.core.logger import get_logger

logger = get_logger()


async def generate_conversation_title(first_message: str) -> str:
    """Generate a short title from the user's first message."""
    cleaned_message = " ".join(first_message.split())
    if not cleaned_message:
        return "New conversation"

    try:
        model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)
        response = await model.ainvoke(
            [
                SystemMessage(
                    content=(
                        "Create a concise title for a chat based on the user's message. "
                        "Use at most 6 words. Return only the title, without quotes."
                    )
                ),
                HumanMessage(content=cleaned_message),
            ]
        )

        if isinstance(response.content, str):
            title = re.sub(r"\s+", " ", response.content).strip().strip("\"'")
            if title:
                return title[:255]
    except Exception:
        logger.warning(
            "Could not generate a conversation title; using the message instead",
            exc_info=True,
        )

    if len(cleaned_message) <= 255:
        return cleaned_message

    fallback = cleaned_message[:252].rsplit(" ", 1)[0].strip()
    return f"{fallback or cleaned_message[:252]}..."
