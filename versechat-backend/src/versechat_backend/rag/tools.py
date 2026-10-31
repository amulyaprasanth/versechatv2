from langchain.tools import tool
from langchain_core.tools.retriever import create_retriever_tool
from pydantic import BaseModel, Field

from versechat_backend.rag.vectorstore import VectorStore
from versechat_backend.rag.wiki_retriever import WikiRetriever

store = VectorStore("./bible/")
vs = store.vectorstore


class WikiSearchInput(BaseModel):
    topic: str = Field(
        description="The Wikipedia article topic/title to search (e.g., 'Jerusalem', 'Quantum computing')"
    )
    query: str = Field(
        description="The specific search question or query to answer using the Wikipedia article content."
    )


retriever = WikiRetriever()

bible_search = create_retriever_tool(
    retriever=vs.as_retriever(search_kwargs={"k": 10}),
    name="bible_search",
    description="Search the bible for relavant verses",
    response_format="content_and_artifact",
)


@tool(
    "wiki_retriever",
    description="Search wikipedia for historical and archaeological information",
)
async def wiki_tool(topic: str, query: str) -> str:
    """Userful for retrieving factual context from Wikipedia for a specific topic"""

    docs = await retriever.ainvoke(query=query, topic=topic)

    if not docs:
        return "No relavant information found on Wikipedia for this topic."

    return "\n\n".join([doc.page_content for doc in docs])


if __name__ == "__main__":
    # result = wiki_tool.invoke(
    #     input="What is the historical significance of Jerusalem in ancient times?"
    # )
    # print(result)
    result = bible_search.invoke("john 3 16")
    print(result)
