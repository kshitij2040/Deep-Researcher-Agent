# /academic-rag-agent/retrieval.py
import os
from dotenv import load_dotenv
# LlamaIndex Imports
from llama_index.core import (
    StorageContext,
    load_index_from_storage,
    QueryBundle,
    Settings
)
from llama_index.core.retrievers import BaseRetriever, VectorIndexRetriever
# Temporarily comment out BM25 due to compatibility issues
# from llama_index.retrievers.bm25 import BM25Retriever
# Temporarily comment out ColBERT due to size constraints
# from llama_index.postprocessor.colbert_rerank import ColbertRerank
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# Qdrant imports
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
# Configuration Import
import config

# Load environment variables
load_dotenv()

def get_qdrant_collection_name():
    """Auto-detect the Qdrant collection name"""
    try:
        client = qdrant_client.QdrantClient(path=config.QDRANT_PATH)
        collections = client.get_collections()
        
        if len(collections.collections) == 0:
            raise ValueError("No Qdrant collections found")
        elif len(collections.collections) == 1:
            collection_name = collections.collections[0].name
            print(f"Auto-detected Qdrant collection: {collection_name}")
            return collection_name
        else:
            # Multiple collections, prefer common names
            collection_names = [c.name for c in collections.collections]
            preferred_names = ["text_collection", "documents", "default"]
            
            for preferred in preferred_names:
                if preferred in collection_names:
                    print(f"Using preferred collection: {preferred}")
                    return preferred
            
            # Fall back to first collection
            collection_name = collection_names[0]
            print(f"Using first available collection: {collection_name}")
            return collection_name
            
    except Exception as e:
        print(f"Error detecting collection name: {e}")
        return "text_collection"  # Default fallback

class HybridRetriever(BaseRetriever):
    """Custom retriever that fuses results from vector and keyword search."""
    
    def __init__(self, vector_retriever, bm25_retriever):
        self._vector_retriever = vector_retriever
        self._bm25_retriever = bm25_retriever
        super().__init__()
    
    def _retrieve(self, query_bundle: QueryBundle):
        vector_nodes = self._vector_retriever.retrieve(query_bundle)
        bm25_nodes = self._bm25_retriever.retrieve(query_bundle)
        
        all_nodes = []
        node_ids = set()
        
        for n in bm25_nodes + vector_nodes:
            if n.node.node_id not in node_ids:
                all_nodes.append(n)
                node_ids.add(n.node.node_id)
        
        return all_nodes

def setup_query_engine():
    """
    Loads the persisted index and sets up the query engine with a hybrid retriever
    and a ColBERT re-ranker.
    """
    if not os.path.exists(config.STORAGE_DIR):
        raise FileNotFoundError(
            f"Storage directory '{config.STORAGE_DIR}' not found. "
            "Please run 'python ingestion.py' first."
        )

    # Configure Settings with Gemini LLM
    print("Configuring Gemini LLM and embeddings...")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    
    # Setup Gemini LLM
    try:
        llm = Gemini(model=config.LLM_MODEL, api_key=api_key)
        print(f"✅ Successfully initialized Gemini model: {config.LLM_MODEL}")
    except Exception as e:
        print(f"⚠️  Gemini not available: {e}")
        print("Please check your API key and internet connection")
        llm = None
    
    Settings.llm = llm
    Settings.embed_model = HuggingFaceEmbedding(model_name=config.EMBED_MODEL)

    print("Setting up Qdrant vector store...")
    # Auto-detect collection name
    collection_name = get_qdrant_collection_name()
    
    # Initialize Qdrant client and vector store
    client = qdrant_client.QdrantClient(path=config.QDRANT_PATH)
    vector_store = QdrantVectorStore(client=client, collection_name=collection_name)

    print("Loading index from storage...")
    try:
        # Create storage context with the vector store
        storage_context = StorageContext.from_defaults(
            persist_dir=config.STORAGE_DIR,
            vector_store=vector_store
        )
        index = load_index_from_storage(storage_context)
        print("✅ Index loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading index: {e}")
        raise

    # --- Initialize Retrievers ---
    vector_retriever = VectorIndexRetriever(index=index, similarity_top_k=config.VECTOR_TOP_K)
    
    # Get nodes from the docstore
    nodes = list(storage_context.docstore.docs.values())
    if not nodes:
        raise ValueError("No documents found in the docstore. Please run 'python ingestion.py' first.")
    
    # Temporarily disable BM25 due to compatibility issues
    # bm25_retriever = BM25Retriever.from_defaults(nodes=nodes, similarity_top_k=config.BM25_TOP_K)
    # hybrid_retriever = HybridRetriever(vector_retriever, bm25_retriever)
    
    # Use only vector retriever for now
    hybrid_retriever = vector_retriever

    # --- Initialize ColBERT Re-ranker (disabled for deployment) ---
    # Temporarily disabled due to package size constraints
    print("⚠️  ColBERT reranker disabled for deployment, using basic query engine")
    # Fallback to basic query engine without reranker
    query_engine = RetrieverQueryEngine.from_args(
        retriever=hybrid_retriever,
    )
    print("✅ Vector query engine is ready.")

    return query_engine