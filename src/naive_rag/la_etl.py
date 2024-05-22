import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from src.naive_rag.constants import PDF_FILENAME


# In LangChain 0.2, langchain package no longer requires langchain-community
# and some integrations happen in langchain-[partner] (but some not)
# See https://python.langchain.com/v0.2/docs/versions/overview/#tldr
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.embeddings import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Qdrant


def _xform_and_ingest(
        documents: list[Document],
        text_splitter: TextSplitter,
        embed_model: Embeddings,
        collection_name: str
) -> None:
    """Takes list of documents, does transforms, and feeds into db

    :param documents: the document data structure before chunking
    :param text_splitter: the LangChain TextSplitter that splits docs into chunks
    :param embed_model: embedding model on both the chunks and the query later
    :param collection_name: the collection name to use in Qdrant
    :return:
    """
    # Need Start db via my "run-qdrant.sh" beforehand

    # Step 1: split documents into chunks
    nodes = text_splitter.split_documents(documents)

    # Step 2: feed into DB
    Qdrant.from_documents(
        host="localhost",
        port=6333,
        documents=nodes,
        embedding=embed_model,
        collection_name=collection_name
    )


def _load_file() -> list[Document]:
    # Its DirectoryLoader does not seem to use different loader for different ext
    documents = PyPDFLoader(PDF_FILENAME).load()

    return documents


def etl():
    documents = _load_file()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512, chunk_overlap=128
    )

    embed_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    _xform_and_ingest(
        documents=documents,
        text_splitter=text_splitter,
        embed_model=embed_model,
        collection_name="naive_rag_la"
    )


if __name__ == '__main__':
    etl()