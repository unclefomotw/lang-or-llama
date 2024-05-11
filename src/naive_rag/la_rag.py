import os

from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from qdrant_client import QdrantClient

from src.naive_rag.constants import SYSTEM_PROMPT
from src.naive_rag.constants import USER_PROMPT


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
