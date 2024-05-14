import logging
import os
import sys

from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.retrieval import create_retrieval_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from qdrant_client import QdrantClient

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

# From the LangChain documentation
CONDENSE_PROMPT = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is.
"""

QA_PROMPT = """You are an assistant for question-answering tasks. \
Use the following pieces of retrieved context to answer the question. \
If you don't know the answer, just say that you don't know. \
Use three sentences maximum and keep the answer concise.\

{context}
"""

# Lazy implementation to maintain chat history of different ids
STORE = dict()


def _get_memory(session_id="foobar-default") -> BaseChatMessageHistory:
    """Returns memory of the session

    :param session_id: The keyname is magic unless override `history_factory_config`
                       in `RunnableWithMessageHistory`
    :return:
    """
    if session_id not in STORE:
        STORE[session_id] = ChatMessageHistory()
    return STORE[session_id]


def _get_customized_llm():
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0001)


def _get_retriever():
    embed_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    db_client = QdrantClient(host="localhost", port=6333)
    vector_store = Qdrant(
        collection_name="chat_rag_la",
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
    llm = _get_customized_llm()

    condense_prompt = ChatPromptTemplate.from_messages([
        ("system", CONDENSE_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")  # magic word in create_history_aware_retriever
    ])

    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", QA_PROMPT),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])

    # Condense (using LangChain's helper function)
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, condense_prompt
    )

    # Answer (using 2 LangChain's helper function)
    question_answer_chain = create_stuff_documents_chain(
        llm, qa_prompt
    )
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain
    )

    # Manage chat message history for rag_chain
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        _get_memory,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )

    print("====== conversation pass 1 ======")
    response_1 = conversational_rag_chain.invoke(
        input={"input": "要怎麼申請長照2.0？"},
        config={
            "configurable": {"session_id": "user-24601-conv-1337"}
        }
    )
    print(response_1["answer"])

    print("====== conversation pass 2 ======")
    response_2 = conversational_rag_chain.invoke(
        input={"input": "可以再給更多資訊，解釋更清楚嗎？"},
        config={
            "configurable": {"session_id": "user-24601-conv-1337"}
        }
    )
    print(response_2["answer"])

    print("====== conversation pass 3 ======")
    response_3 = conversational_rag_chain.invoke(
        input={"input": "我剛剛問了什麼問題？"},
        config={
            "configurable": {"session_id": "user-24601-conv-1337"}
        }
    )
    print(response_3["answer"])


if __name__ == '__main__':
    query()
