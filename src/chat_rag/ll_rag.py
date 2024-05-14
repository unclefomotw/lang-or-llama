import logging
import os
import sys

from llama_index.core import VectorStoreIndex
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core.indices.vector_store import VectorIndexRetriever
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))


def _get_memory(chat_store_key="foobar-default"):
    return ChatMemoryBuffer.from_defaults(chat_store_key=chat_store_key)


def _get_customized_llm():
    return OpenAI(model="gpt-3.5-turbo", temperature=0.0001)


def _get_retriever():
    db_client = QdrantClient(host="localhost", port=6333)
    vector_store = QdrantVectorStore(
        collection_name="chat_rag_ll",
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
    retriever = _get_retriever()
    llm = _get_customized_llm()
    memory = _get_memory("user-24601-conv-1337")

    # Dissect from index.as_chat_engine(chat_mode, llm, **kwargs)
    # for clearer retriever assignment
    # This internally calculates LLM context limit so that the history
    # stuffed in the "Answering" call can still fit after prepend with the retrieved knowledge
    chat_engine = CondensePlusContextChatEngine.from_defaults(
        retriever=retriever,
        llm=llm,
        memory=memory,
        # context_prompt=
        # condense_prompt=
        # node_postprocessors=
    )

    print("====== conversation pass 1 ======")
    response = chat_engine.chat("要怎麼申請長照2.0？")
    print(response)

    print("====== conversation pass 2 ======")
    response_2 = chat_engine.chat("可以再給更多資訊，解釋更清楚嗎？")
    print(response_2)

    print("====== conversation pass 3 ======")
    response_3 = chat_engine.chat("我剛剛問了什麼問題？")
    print(response_3)

    # One challenge in chat-like RAG is indirect requests such as "explain more"
    # Because "explain more" can be limited to retrieved information, where naive retrieval
    # may not recognize the intention behind.
    # As for "What did I ask", it can be answered from chat history using memory


if __name__ == '__main__':
    query()
