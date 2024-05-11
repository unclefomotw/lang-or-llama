import os

from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TransformComponent
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

from src.naive_rag.constants import PDF_FILENAME


def _xform_and_ingest(
        documents: list[Document],
        transformations: list[TransformComponent],
        collection_name: str
) -> None:
    """Takes list of documents, does transforms, and feeds into db

    :param documents: the document data structure before chunking
    :param transformations: transforms documents into chunks/nodes
    :param collection_name: the collection name to use in Qdrant
    """

    # Start db via my "run-qdrant.sh"
    db_client = QdrantClient(host="localhost", port=6333)

    # Storage objects of llama-index
    # pass the DB client to the vector store
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=db_client
    )

    # Use pipeline to transform documents into nodes and feed into DB
    pipeline = IngestionPipeline(
        transformations=transformations,
        vector_store=vector_store
    )
    pipeline.run(documents=documents)


def _load_file() -> list[Document]:
    # Detects ext; use pypdf for .pdf
    documents = SimpleDirectoryReader(
        input_files=[PDF_FILENAME]
    ).load_data()

    return documents


def etl():
    documents = _load_file()

    # A function that splits documents into chunks
    # (each of which is of its size that honors sentence boundary)
    node_parser = SentenceSplitter(
        chunk_size=512, chunk_overlap=128
    )

    # Use HuggingFace embedding, and use HF HUB standard cache dir
    # (by default it's cached under ~/Library/Caches/llama_index/)
    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    _xform_and_ingest(
        documents=documents,
        transformations=[node_parser, embed_model],
        collection_name="naive_rag_ll"
    )


if __name__ == '__main__':
    etl()
