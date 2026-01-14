# Nerthus AI Example Document

## Introduction

This is a sample document to demonstrate the capabilities of Nerthus AI, a RAG (Retrieval-Augmented Generation) system built with LangChain, LangGraph, and ChromaDB.

## What is Nerthus?

Nerthus is an intelligent AI assistant library and interactive CLI that provides intelligence, contextual analysis, and orchestration capabilities developed for the Nerthus ecosystem.

## Key Features

### 1. Document Ingestion
Nerthus can process multiple document formats including:
- PDF documents
- Text files
- Word documents (DOCX)
- Markdown files

### 2. Vector Storage
Documents are stored in ChromaDB, a powerful vector database that enables efficient similarity search and retrieval.

### 3. RAG Pipeline
The Retrieval-Augmented Generation pipeline consists of:
1. Document chunking with configurable size and overlap
2. Embedding generation using OpenAI embeddings
3. Vector storage in ChromaDB
4. Semantic search for relevant context
5. LLM-based answer generation with retrieved context

### 4. Design Patterns

Nerthus implements several important design patterns:

#### Singleton Pattern
The Settings class ensures only one configuration instance exists throughout the application.

#### Facade Pattern
NerthusSession provides a simplified interface to the complex RAG system, making it easy to use.

#### Factory Pattern
DocumentLoaderFactory creates appropriate loaders based on file type automatically.

## Use Cases

Nerthus can be used for:
- Knowledge base question answering
- Document analysis and summarization
- Information retrieval from large document collections
- Contextual AI assistance

## Technical Stack

- **LangChain**: Framework for developing applications with LLMs
- **LangGraph**: State graph implementation for complex workflows
- **ChromaDB**: Vector database for embeddings storage
- **Pydantic**: Data validation and settings management
- **Click**: Command-line interface framework

## Getting Started

To get started with Nerthus:

1. Install dependencies from requirements.txt
2. Configure your OpenAI API key in .env
3. Ingest your documents using the CLI
4. Start querying your knowledge base

## Example Workflow

```bash
# Ingest documents
python nerthus_cli.py ingest ./documents

# Query the system
python nerthus_cli.py query "What is Nerthus?"

# Start interactive session
python nerthus_cli.py interactive
```

## Conclusion

Nerthus AI provides a powerful, flexible, and easy-to-use RAG system that can be integrated into various applications requiring intelligent document processing and question answering capabilities.
