# /academic-rag-agent/config.py
import os

# --- File Paths ---
# Use environment variables for production, fallback to local paths for development
PDF_DIRECTORY = os.getenv("PDF_DIRECTORY", "./data")
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
MARKDOWN_DIR = os.path.join("./output", "parsed_markdown")
IMAGE_DIR = os.path.join("./output", "extracted_images")
QDRANT_PATH = os.path.join(STORAGE_DIR, "qdrant_db")
DOCSTORE_PATH = os.path.join(STORAGE_DIR, "docstore.json")

# --- Model Configuration ---
# Gemini LLM Configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")  # or "gemini-pro"
LLM_TYPE = os.getenv("LLM_TYPE", "gemini")  # Options: "gemini", "ollama", "huggingface", "none"
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")  # Local embedding model
RERANKER_MODEL = os.getenv("RERANKER_MODEL", "colbert-ir/colbertv2.0")

# --- Deep Research Configuration ---
MAX_REASONING_STEPS = int(os.getenv("MAX_REASONING_STEPS", "10"))
ENABLE_QUERY_DECOMPOSITION = os.getenv("ENABLE_QUERY_DECOMPOSITION", "True").lower() == "true"
ENABLE_MULTI_SOURCE_SYNTHESIS = os.getenv("ENABLE_MULTI_SOURCE_SYNTHESIS", "True").lower() == "true"
RESEARCH_OUTPUT_DIR = os.getenv("RESEARCH_OUTPUT_DIR", "./research_outputs")

# --- Retrieval and Reranking Configuration ---
VECTOR_TOP_K = int(os.getenv("VECTOR_TOP_K", "10"))
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "10"))
RERANKER_TOP_N = int(os.getenv("RERANKER_TOP_N", "5"))

# --- Chunk Configuration ---
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50