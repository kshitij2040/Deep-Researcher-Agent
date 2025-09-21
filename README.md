# Deep Research Agent 🔬

### Core Capabilities
- **🧠 Multi-Step Reasoning:** Automatically decomposes complex queries into logical sub-tasks
- **📚 Multi-Source Synthesis:** Combines information from multiple documents into coherent research reports  
- **🔍 Deep Query Analysis:** Pattern-based query understanding (comparison, process, pros/cons analysis)
- **💬 Interactive Query Refinement:** Suggests follow-up questions for deeper exploration
- **📄 Research Export:** Export results in PDF and Markdown formats with structured data

### Technical Excellence
- **🔧 Local-First Architecture:** No external API dependencies required
- **🏗️ Hybrid Retrieval:** Combines semantic (vector) and keyword (BM25) search
- **⚡ Advanced Re-ranking:** ColBERT re-ranking for improved relevance
- **🤖 Flexible LLM Support:** Works with Ollama, HuggingFace, or embeddings-only mode
- **💾 Efficient Storage:** Qdrant vector database with smart indexing

## 🛠️ Setup

1. **Clone and Setup Environment:**
   ```bash
   git clone <>
   cd Stochastic-RAG-AGENT-main
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Optional: Install Ollama for Local LLM** (Recommended)
   ```bash
   # Install Ollama from https://ollama.ai/
   # Then pull a model:
   ollama pull llama3.1:8b
   ```

3. **Prepare Your Documents:**
   ```bash
   # Place PDF documents in the ./data directory
   mkdir data
   # Copy your research papers to ./data/
   ```

## 🎯 Usage

### 1. Build Knowledge Base
```bash
python ingestion.py
```
This creates local embeddings and indexes your documents.

### 2. Start Deep Research Agent
```bash
python main.py
```

### 3. Research Commands
- **Regular Query:** Just ask your question naturally
- **Deep Analysis:** `deep [your question]` - Triggers comprehensive multi-step analysis  
- **Query Refinement:** `refine [your question]` - Get follow-up suggestions
- **Export Research:** `export` - Save current research session
- **Exit:** `quit` or `exit`

## 🔬 Research Capabilities Examples

### Multi-Step Query Decomposition
```
Query: "Compare machine learning approaches for natural language processing"

→ Decomposes into:
1. Background research on ML approaches
2. NLP-specific ML techniques analysis  
3. Comparative analysis with pros/cons
4. Practical applications and use cases
```

### Deep Synthesis Reports
The agent creates comprehensive reports with:
- **Research Strategy:** Shows reasoning steps
- **Sub-Analysis Sections:** Detailed breakdown of each aspect
- **Source Integration:** Combines multiple document insights
- **Export Options:** Markdown, JSON, or PDF formats

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │───▶│ Query Decomposer │───▶│ Multi-Step      │
└─────────────────┘    └──────────────────┘    │ Reasoning       │
                                               └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐           ▼
│ Research Report │◀───│   Synthesizer    │    ┌─────────────────┐
│   & Export      │    └──────────────────┘    │ Hybrid Retrieval│
└─────────────────┘                            │ Vector + BM25   │
                                               └─────────────────┘
                                                        │
┌─────────────────┐    ┌──────────────────┐           ▼
│ Local Documents │───▶│ Qdrant Vector DB │    ┌─────────────────┐
│ (PDF Processing)│    │ + ColBERT Rerank │    │ Document Results│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Configuration Options

Edit `config.py` to customize:

```python
# LLM Configuration
LLM_MODEL = "llama3.1:8b"  # Ollama model
LLM_TYPE = "ollama"        # "ollama", "huggingface", "none"

# Research Configuration  
MAX_REASONING_STEPS = 10
ENABLE_QUERY_DECOMPOSITION = True
ENABLE_MULTI_SOURCE_SYNTHESIS = True
RESEARCH_OUTPUT_DIR = "./research_outputs"

# Retrieval Configuration
VECTOR_TOP_K = 10
BM25_TOP_K = 10  
RERANKER_TOP_N = 5
```

## 🔄 Deployment Modes

### Mode 1: Full Local (Recommended)
- **LLM:** Ollama (llama3.1:8b)
- **Embeddings:** Local HuggingFace models
- **Vector DB:** Local Qdrant
- **Benefits:** Complete privacy, no API costs, fast response

### Mode 2: Embeddings-Only  
- **LLM:** None (simple rule-based responses)
- **Embeddings:** Local HuggingFace models
- **Vector DB:** Local Qdrant
- **Benefits:** Lightweight, still performs good retrieval

### Mode 3: Hybrid (Advanced Users)
- **LLM:** Custom local model integration
- **Embeddings:** Custom embedding models
- **Vector DB:** External Qdrant instance

## 🚨 Troubleshooting

### Common Issues

1. **"Ollama not available"**
   ```bash
   # Install Ollama and pull model
   ollama pull llama3.1:8b
   ```

2. **"No Qdrant collections found"**
   ```bash
   # Re-run ingestion
   python ingestion.py
   ```

3. **"Storage directory not found"**
   ```bash
   # Build knowledge base first
   python ingestion.py
   ```

4. **Slow performance**
   - Reduce `VECTOR_TOP_K` and `BM25_TOP_K` in config.py
   - Use smaller embedding models
   - Enable hardware acceleration for embeddings

## 📊 Performance Notes

- **Processing Speed:** ~1-3 seconds per query (local setup)
- **Memory Usage:** ~2-4GB RAM (depending on model size)
- **Storage Requirements:** ~100MB per 1000 document pages
- **Concurrent Users:** Supports multiple sessions

## 🤝 Contributing

This implementation demonstrates key concepts for the Deep Researcher Agent challenge:

1. **Local Processing:** No external dependencies for core functionality
2. **Scalable Architecture:** Modular design for easy extension
3. **Multi-Step Reasoning:** Sophisticated query decomposition
4. **Research Synthesis:** Coherent report generation
5. **Export Capabilities:** Multiple output formats

## 📄 License

[Add your license information here]

## 🔗 References

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [Ollama Local LLM](https://ollama.ai/)
- [Qdrant Vector Database](https://qdrant.tech/)
- [HuggingFace Transformers](https://huggingface.co/transformers/)# Deep-Researcher-Agent
