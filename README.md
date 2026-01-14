# Nerthus AI

Biblioteca Python e CLI interativo que provê as capacidades de inteligência, análise contextual e orquestração desenvolvidas para o ecossistema Nerthus.

## 🌟 Features

- **RAG (Retrieval-Augmented Generation)**: Advanced question-answering system with context retrieval
- **LangChain/LangGraph Integration**: State-based workflow management with LangGraph
- **ChromaDB Vector Store**: Persistent vector database for efficient document retrieval
- **Multiple Document Formats**: Support for PDF, TXT, DOCX, and Markdown files
- **Design Patterns**: 
  - Singleton pattern for Settings management
  - Facade pattern for NerthusSession
  - Factory pattern for Document Loaders
- **Interactive CLI**: User-friendly command-line interface
- **Configurable**: YAML-based prompts and environment-based configuration

## 📋 Requirements

- Python 3.8+
- OpenAI API key

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/strondata/nerthus-ai.git
cd nerthus-ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## 💻 Usage

### CLI Commands

#### Ingest Documents
```bash
# Ingest a single file
python nerthus_cli.py ingest path/to/document.pdf

# Ingest a directory
python nerthus_cli.py ingest path/to/documents/

# Use a specific collection
python nerthus_cli.py ingest path/to/docs/ --collection my_collection

# Add manual tags (repeatable)
python nerthus_cli.py ingest path/to/docs/ --collection legacy_lab_2023 --tag extrusao --tag 2023
```

#### Query the System
```bash
# Simple query
python nerthus_cli.py query "What is the main topic of the documents?"

# Query with verbose output (show sources)
python nerthus_cli.py query "Explain the concept" --verbose

# Query with custom model
python nerthus_cli.py query "Your question" --model gpt-4
```

#### Interactive Session
```bash
# Start interactive mode
python nerthus_cli.py interactive

# Interactive with specific collection
python nerthus_cli.py interactive --collection my_docs
```

#### Set Collection Context
```bash
# Set active collection context
python nerthus_cli.py context legacy_lab_2023
```

#### Generate Report
```bash
# Generate extrusion log report
python nerthus_cli.py report --type extrusion_log --collection legacy_lab_2023
```

#### View Statistics
```bash
# Show session statistics
python nerthus_cli.py stats
```

#### View Configuration
```bash
# Show current configuration
python nerthus_cli.py config
```

#### Clear Collection
```bash
# Clear all documents from collection
python nerthus_cli.py clear
```

### Python API

```python
from session import NerthusSession

# Initialize session
session = NerthusSession()
session.initialize()

# Ingest documents
result = session.ingest_directory("./documents")
print(f"Ingested {result['total_chunks']} chunks from {result['total_files']} files")

# Query the system
response = session.query("What are the key findings?")
print(response['answer'])

# Get statistics
stats = session.get_stats()
print(f"Collection has {stats['document_count']} documents")
```

## 🏗️ Architecture

### Design Patterns

#### Singleton Pattern (Settings)
The `Settings` class implements the Singleton pattern to ensure only one configuration instance exists throughout the application lifecycle.

```python
from config import get_settings

settings = get_settings()  # Always returns the same instance
```

#### Facade Pattern (NerthusSession)
The `NerthusSession` class provides a simplified interface to the complex RAG system, hiding the complexity of document ingestion, embedding, and retrieval.

```python
from session import NerthusSession

session = NerthusSession()
session.initialize()
result = session.query("Your question")
```

#### Factory Pattern (Document Loaders)
The `DocumentLoaderFactory` creates appropriate document loaders based on file type.

```python
from ingest import DocumentLoaderFactory

loader = DocumentLoaderFactory.create_loader("document.pdf")
documents = loader.load("document.pdf")
```

### Components

- **config.py**: Configuration management with Pydantic and YAML loader
- **session.py**: Facade class for simplified session management
- **ingest.py**: Document ingestion with Factory pattern for loaders
- **rag_chain.py**: LangGraph-based state graph for RAG pipeline
- **nerthus_cli.py**: Click-based CLI interface
- **prompts.yaml**: YAML configuration for system prompts and templates

## 📁 Project Structure

```
nerthus-ai/
├── config.py           # Settings with Singleton pattern
├── session.py          # NerthusSession Facade class
├── ingest.py          # Document ingestion with Factory pattern
├── rag_chain.py       # LangGraph State Graph implementation
├── nerthus_cli.py     # CLI interface
├── prompts.yaml       # Prompt configurations
├── requirements.txt   # Python dependencies
├── setup.py          # Package setup
├── .env.example      # Environment template
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## ⚙️ Configuration

### Environment Variables (.env)

```env
OPENAI_API_KEY=your-api-key-here
MODEL_NAME=gpt-3.5-turbo
TEMPERATURE=0.7
CHROMA_PERSIST_DIRECTORY=./chroma_db
COLLECTION_NAME=general
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_RESULTS=4
REPORT_CONTEXT_DOCUMENTS=5
```

### Prompts (prompts.yaml)

Customize system prompts and templates in `prompts.yaml`:

```yaml
system_prompts:
  default: "Your default system prompt"
  contextual: "Your contextual prompt with {context}"

templates:
  query_prompt: "Question: {question}"
```

## 🧪 Supported Document Formats

- **PDF** (.pdf)
- **Text** (.txt)
- **Word** (.docx)
- **Markdown** (.md)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/)
- Powered by [LangGraph](https://github.com/langchain-ai/langgraph)
- Vector storage by [ChromaDB](https://www.trychroma.com/)
- CLI framework by [Click](https://click.palletsprojects.com/)
