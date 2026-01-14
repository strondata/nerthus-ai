"""
Document ingestion module for Nerthus AI.
Implements Factory pattern for document loaders.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any
from enum import Enum

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
)
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from config import get_settings
from extractors import MetadataExtractor


class DocumentType(Enum):
    """Supported document types."""
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    MD = "md"


class DocumentLoaderInterface(ABC):
    """Abstract base class for document loaders."""
    
    @abstractmethod
    def load(self, file_path: str) -> List[Document]:
        """Load documents from file."""
        pass


class PDFDocumentLoader(DocumentLoaderInterface):
    """Loader for PDF documents."""
    
    def load(self, file_path: str) -> List[Document]:
        """Load PDF document."""
        loader = PyPDFLoader(file_path)
        return loader.load()


class TextDocumentLoader(DocumentLoaderInterface):
    """Loader for text documents."""
    
    def load(self, file_path: str) -> List[Document]:
        """Load text document."""
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()


class DocxDocumentLoader(DocumentLoaderInterface):
    """Loader for DOCX documents."""
    
    def load(self, file_path: str) -> List[Document]:
        """Load DOCX document."""
        loader = Docx2txtLoader(file_path)
        return loader.load()


class MarkdownDocumentLoader(DocumentLoaderInterface):
    """Loader for Markdown documents."""
    
    def load(self, file_path: str) -> List[Document]:
        """Load Markdown document."""
        loader = TextLoader(file_path, encoding='utf-8')
        return loader.load()


class DocumentLoaderFactory:
    """
    Factory class for creating document loaders.
    Implements Factory pattern.
    """
    
    _loaders = {
        DocumentType.PDF: PDFDocumentLoader,
        DocumentType.TXT: TextDocumentLoader,
        DocumentType.DOCX: DocxDocumentLoader,
        DocumentType.MD: MarkdownDocumentLoader,
    }
    
    @classmethod
    def create_loader(cls, file_path: str) -> DocumentLoaderInterface:
        """
        Create appropriate document loader based on file extension.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            DocumentLoaderInterface instance
            
        Raises:
            ValueError: If file type is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower().lstrip('.')
        
        try:
            doc_type = DocumentType(extension)
        except ValueError:
            raise ValueError(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join([t.value for t in DocumentType])}"
            )
        
        loader_class = cls._loaders.get(doc_type)
        if loader_class is None:
            raise ValueError(f"No loader available for document type: {doc_type}")
        
        return loader_class()
    
    @classmethod
    def get_supported_extensions(cls) -> List[str]:
        """Get list of supported file extensions."""
        return [doc_type.value for doc_type in DocumentType]


class ChromaDocumentStore:
    """Repository pattern wrapper for Chroma collections."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        embedding_function: Optional[OpenAIEmbeddings] = None,
    ):
        settings = get_settings()
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.embedding_function = embedding_function or OpenAIEmbeddings()

    def get_collection(self, collection_name: str) -> Chroma:
        return Chroma(
            collection_name=collection_name,
            embedding_function=self.embedding_function,
            persist_directory=self.persist_directory,
        )

    def add_documents(
        self,
        chunks: List[Document],
        collection_name: str,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        if metadatas:
            for chunk, metadata in zip(chunks, metadatas):
                chunk.metadata = {**chunk.metadata, **metadata}

        vectorstore = self.get_collection(collection_name)
        vectorstore.add_documents(chunks)


class DocumentIngester:
    """Main class for document ingestion into ChromaDB."""
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """
        Initialize document ingester.
        
        Args:
            persist_directory: Directory for ChromaDB persistence
            collection_name: Name of the ChromaDB collection
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between chunks
        """
        self.settings = get_settings()
        
        self.persist_directory = persist_directory or self.settings.chroma_persist_directory
        self.collection_name = collection_name or self.settings.collection_name
        self.chunk_size = chunk_size or self.settings.chunk_size
        self.chunk_overlap = chunk_overlap or self.settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
        
        self.embeddings = OpenAIEmbeddings()
        self.store = ChromaDocumentStore(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
        )
        self.metadata_extractor = MetadataExtractor()

    def _resolve_collection(self, collection_name: Optional[str]) -> str:
        resolved = collection_name or self.collection_name
        if resolved not in self.settings.available_collections:
            raise ValueError(f"Invalid collection name: {resolved}")
        return resolved
    
    def ingest_file(
        self,
        file_path: str,
        collection_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> int:
        """
        Ingest a single document file.
        
        Args:
            file_path: Path to the document file
            collection_name: Target collection name
            tags: Manual tags to attach to metadata
            
        Returns:
            Number of chunks ingested
        """
        collection_name = self._resolve_collection(collection_name)
        manual_tags = list(tags) if tags else []

        # Create loader using factory
        loader = DocumentLoaderFactory.create_loader(file_path)
        
        # Load document
        documents = loader.load(file_path)

        extracted_meta: Dict[str, Any] = {}
        if documents:
            try:
                extracted_meta = self.metadata_extractor.extract(
                    documents[0].page_content,
                    Path(file_path).name,
                )
            except Exception:
                extracted_meta = {}
        if not isinstance(extracted_meta, dict):
            extracted_meta = {}

        full_metadata = {
            **extracted_meta,
            "manual_tags": manual_tags,
            "collection": collection_name,
            "source": file_path,
        }
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        for chunk in chunks:
            chunk.metadata = {**chunk.metadata, **full_metadata}
        
        # Add to vector store
        self.store.add_documents(
            chunks=chunks,
            collection_name=collection_name,
        )
        
        return len(chunks)
    
    def ingest_directory(
        self,
        directory_path: str,
        collection_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> dict:
        """
        Ingest all supported documents from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            collection_name: Target collection name
            tags: Manual tags to attach to metadata
            
        Returns:
            Dictionary with ingestion results
        """
        directory = Path(directory_path)
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        supported_extensions = DocumentLoaderFactory.get_supported_extensions()
        results = {
            "total_files": 0,
            "total_chunks": 0,
            "files_processed": [],
            "errors": []
        }
        
        for ext in supported_extensions:
            for file_path in directory.rglob(f"*.{ext}"):
                try:
                    chunks = self.ingest_file(
                        str(file_path),
                        collection_name=collection_name,
                        tags=tags,
                    )
                    results["total_files"] += 1
                    results["total_chunks"] += chunks
                    results["files_processed"].append({
                        "file": str(file_path),
                        "chunks": chunks
                    })
                except Exception as e:
                    results["errors"].append({
                        "file": str(file_path),
                        "error": str(e)
                    })
        
        return results
    
    def get_vectorstore(self, collection_name: Optional[str] = None) -> Chroma:
        """Get the ChromaDB vector store."""
        resolved = self._resolve_collection(collection_name)
        return self.store.get_collection(resolved)
