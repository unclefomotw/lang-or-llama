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
    # Start db via my "run-qdrant.sh"
    db_client = QdrantClient(host="localhost", port=6333)

    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        client=db_client
    )

    pipeline = IngestionPipeline(
        transformations=transformations,
        vector_store=vector_store
    )
    pipeline.run(documents=documents)


def _load_file() -> list[Document]:
    documents = SimpleDirectoryReader(input_files=[PDF_FILENAME]).load_data()

    # Remove unnecessary metadata that will go into the prompt later
    for doc in documents:
        doc.excluded_llm_metadata_keys.extend(["page_label", "file_path"])
        doc.excluded_embed_metadata_keys.extend(["page_label", "file_path"])

    return documents


def etl():
    documents = _load_file()

    node_parser = SentenceSplitter(
        chunk_size=512, chunk_overlap=128
    )

    embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-base-zh-v1.5",
        cache_folder=os.path.expanduser("~/.cache/huggingface/hub")
    )

    _xform_and_ingest(
        documents=documents,
        transformations=[node_parser, embed_model],
        collection_name="chat_rag_ll"
    )


if __name__ == '__main__':
    etl()
