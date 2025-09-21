# /academic-rag-agent/ingestion.py

import os
import subprocess
from pathlib import Path
import qdrant_client
from dotenv import load_dotenv
import json

# LlamaIndex Imports
from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    Settings,
)
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
# from llama_index.llms.gemini import Gemini  # Removed: module does not exist
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Utility and Configuration Imports
import pymupdf4llm
import config

# Load environment variables
load_dotenv()

def setup_paths():
    """Create necessary directories if they don't exist."""
    os.makedirs(config.MARKDOWN_DIR, exist_ok=True)
    os.makedirs(config.IMAGE_DIR, exist_ok=True)
    os.makedirs(config.STORAGE_DIR, exist_ok=True)
    print("Directories are set up.")

def parse_documents():
    """
    Parses all PDFs using Nougat for text and PyMuPDF4LLM for images.
    """
    pdf_files = list(Path(config.PDF_DIRECTORY).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {config.PDF_DIRECTORY}. Aborting.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process.")

    # --- 1. Semantic Parsing with Nougat ---
    print("Starting Nougat to parse semantic structure...")
    command = ["nougat", str(config.PDF_DIRECTORY), "-o", config.MARKDOWN_DIR]
    subprocess.run(command, check=True)
    print("Nougat processing complete.")

    # --- 2. Image Extraction with PyMuPDF4LLM ---
    print("Starting PyMuPDF4LLM to extract images...")
    for pdf_path in pdf_files:
        pymupdf4llm.to_markdown(str(pdf_path), write_images=True, image_path=config.IMAGE_DIR)
    print("Image extraction complete.")

def build_and_persist_index():
    """
    Builds a multimodal index from parsed documents and persists it to disk.
    """
    print("Starting to build and persist the index...")
    
    # Configure models explicitly
    llm = OpenAI(model=config.LLM_MODEL, api_key=os.getenv("OPENAI_API_KEY"))
    # llm = Gemini(model=config.LLM_MODEL, api_key=os.getenv("GOOGLE_API_KEY"))  # Removed: Gemini not available
    embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)
    print(f"Using LLM: {config.LLM_MODEL}")
    print(f"Using embedding model: {config.EMBED_MODEL}")
    
    # Set global settings
    Settings.llm = llm
    Settings.embed_model = embed_model
    
    text_docs = SimpleDirectoryReader(config.MARKDOWN_DIR, filename_as_id=True).load_data()
    image_docs = SimpleDirectoryReader(config.IMAGE_DIR, filename_as_id=True).load_data()
    print(f"Loaded {len(text_docs)} text documents and {len(image_docs)} images.")

    docstore = SimpleDocumentStore()
    if os.path.exists(config.DOCSTORE_PATH):
        try:
            docstore = SimpleDocumentStore.from_persist_path(config.DOCSTORE_PATH)
            print("Loaded existing document store.")
        except json.JSONDecodeError:
            print("Docstore file is corrupted or empty. Creating a new one.")
            pass
    else:
        print("Created a new document store.")

    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=3,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )
    
    client = qdrant_client.QdrantClient(path=config.QDRANT_PATH)
    text_store = QdrantVectorStore(client=client, collection_name="text_collection")
    image_store = QdrantVectorStore(client=client, collection_name="image_collection")
    
    storage_context = StorageContext.from_defaults(
        vector_store=text_store,
        image_store=image_store,
        docstore=docstore
    )

    # Explicitly pass the embedding model to ensure it's used
    print("Building index with explicit embedding model...")
    index = VectorStoreIndex.from_documents(
        text_docs + image_docs,
        storage_context=storage_context,
        node_parser=node_parser,
        embed_model=embed_model,  # Explicitly pass the embedding model
        show_progress=True,
    )
    
    index.storage_context.persist(persist_dir=config.STORAGE_DIR)
    print(f"Index and document store have been persisted to {config.STORAGE_DIR}")

if __name__ == "__main__":
    setup_paths()
    parse_documents()
    build_and_persist_index()
    print("Ingestion process complete.")