import os

from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.prompts.base import ChatPromptTemplate
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.naive_rag.constants import SYSTEM_PROMPT
from src.naive_rag.constants import USER_PROMPT


def get_customized_prompt_template():
    """Prompt that passes the question and retrieved context to LLM."""
    system_prompt = ChatMessage(role=MessageRole.SYSTEM, content=SYSTEM_PROMPT)
    user_prompt = ChatMessage(role=MessageRole.USER, content=USER_PROMPT)

    return ChatPromptTemplate(
        message_templates=[system_prompt, user_prompt],
        template_var_mappings={"context_str": "context", "query_str": "query"}
    )


def get_customized_llm():
    """LLM that synthesizes the answer from the prompt"""
    return OpenAI(temperature=0.0001)


def get_retriever():
    db_client = QdrantClient(host="localhost", port=6333)
    vector_store = QdrantVectorStore(
        collection_name="naive_rag_ll",
        client=db_client
    )

    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        embed_model=embed_model
    )

    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=3,
    )

    return retriever


def query():
    retriever = get_retriever()
    prompt_template = get_customized_prompt_template()
    llm = get_customized_llm()

    response_synthesizer = get_response_synthesizer(
        llm=llm,
        text_qa_template=prompt_template,
    )

    query_engine = RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=response_synthesizer
    )

    response = query_engine.query("要怎麼申請長照2.0？")
    print(response)


if __name__ == '__main__':
    query()