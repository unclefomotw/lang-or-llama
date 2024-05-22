import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from src.naive_rag.constants import SYSTEM_PROMPT
from src.naive_rag.constants import USER_PROMPT


# In LangChain 0.2, langchain package no longer requires langchain-community
# and some integrations happen in langchain-[partner] (but some not)
# See https://python.langchain.com/v0.2/docs/versions/overview/#tldr
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Qdrant


def _get_customized_prompt_template():
    """Prompt that passes the question and retrieved context to LLM."""
    return ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT),
        ]
    )


def _get_customized_llm():
    """LLM that synthesizes the answer from the prompt"""
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0001)


def _get_retriever():
    embed_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    db_client = QdrantClient(host="localhost", port=6333)
    vector_store = Qdrant(
        collection_name="naive_rag_la",
        client=db_client,
        embeddings=embed_model
    )

    retriever = vector_store.as_retriever(
        search_kwargs={"k": 3}
    )

    return retriever


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def query():
    retriever = _get_retriever()
    prompt_template = _get_customized_prompt_template()
    llm = _get_customized_llm()

    # The point here is not about the "pipe" operator
    # The point here is their "Runnable" class that hide those batch/stream/... behind
    rag_chain = (
        {'context': retriever | _format_docs, 'query': RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    response = rag_chain.invoke("要怎麼申請長照2.0？")
    print(response)


if __name__ == '__main__':
    query()
