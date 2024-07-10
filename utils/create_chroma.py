"""chroma.py"""

import logging
import os
import shutil
import tempfile
import time

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma


def create_chroma(
    from_file: str, replace: bool = False, persist_to: str = None
) -> Chroma:
    """Create a Chroma instance from a (pdf) file.
    Args:
        - `from_file (str)`: The file to load the Chroma instance from.
        - `replace (optinal bool)`: Whether to replace the existing embeddings or not.
        - `persist_to (optional str)`: The directory to persist the embeddings to.\
            Defaults to `/tmp/__embeddings_{time.time()}`. \n
    Returns:
        `Chroma`: The Chroma instance.
    """
    # base_dir = os.path.dirname(os.path.abspath(__file__))
    persist_dir = persist_to or os.path.join(
        tempfile.gettempdir(), f"_embeddings_{time.time()}"
    )
    embeds = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    if not replace and os.path.exists(persist_dir):
        return Chroma(persist_directory=persist_dir, embedding_function=embeds)
    if replace and os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        os.makedirs(persist_dir)
    loader = PyPDFLoader(from_file)
    text_splitter = CharacterTextSplitter(chunk_size=5000, separator="\n")
    chunks = text_splitter.split_documents(loader.load())
    _chromadb = Chroma.from_documents(chunks, embeds, persist_directory=persist_dir)
    _chromadb.persist()
    logging.info("Embeddings persisted to: %s", persist_dir)
    return _chromadb
