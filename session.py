"""
Session management module for Nerthus AI.
Implements Facade pattern for simplified session management.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path

from config import get_settings, Settings
from ingest import DocumentIngester
from rag_chain import RAGChain


class NerthusSession:
    """
    Facade class for Nerthus AI session management.
    Provides a simplified interface to the RAG system.
    """
    
    def __init__(
        self,
        settings: Optional[Settings] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Initialize Nerthus session.
        
        Args:
            settings: Settings instance (uses singleton if not provided)
            model_name: Override model name
            temperature: Override temperature
        """
        self.settings = settings or get_settings()
        self.model_name = model_name or self.settings.model_name
        self.temperature = temperature or self.settings.temperature
        
        # Initialize components
        self._ingester: Optional[DocumentIngester] = None
        self._rag_chain: Optional[RAGChain] = None
        self._initialized = False
    
    @property
    def ingester(self) -> DocumentIngester:
        """Lazy initialization of document ingester."""
        if self._ingester is None:
            self._ingester = DocumentIngester()
        return self._ingester
    
    @property
    def rag_chain(self) -> RAGChain:
        """Lazy initialization of RAG chain."""
        if self._rag_chain is None:
            self._rag_chain = RAGChain(
                model_name=self.model_name,
                temperature=self.temperature,
            )
        return self._rag_chain
    
    def initialize(self) -> "NerthusSession":
        """
        Initialize the session (ensure all components are ready).
        
        Returns:
            Self for method chaining
        """
        # Trigger lazy initialization
        _ = self.ingester
        _ = self.rag_chain
        self._initialized = True
        return self
    
    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a single document file.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Dictionary with ingestion results
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        chunks = self.ingester.ingest_file(file_path)
        
        return {
            "success": True,
            "file": str(file_path),
            "chunks": chunks,
            "message": f"Successfully ingested {chunks} chunks from {file_path_obj.name}"
        }
    
    def ingest_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Ingest all supported documents from a directory.
        
        Args:
            directory_path: Path to directory containing documents
            
        Returns:
            Dictionary with ingestion results
        """
        directory = Path(directory_path)
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        results = self.ingester.ingest_directory(directory_path)
        
        return {
            "success": True,
            "directory": str(directory_path),
            "total_files": results["total_files"],
            "total_chunks": results["total_chunks"],
            "files_processed": results["files_processed"],
            "errors": results["errors"],
            "message": f"Ingested {results['total_files']} files ({results['total_chunks']} chunks)"
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Execute a RAG query.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and context
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        result = self.rag_chain.query(question)
        
        return {
            "success": True,
            "question": question,
            "answer": result["answer"],
            "context": result["context"],
            "num_sources": len(result["context"])
        }
    
    def stream_query(self, question: str):
        """
        Execute a RAG query with streaming.
        
        Args:
            question: User question
            
        Yields:
            State updates during execution
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        yield from self.rag_chain.stream_query(question)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with session stats
        """
        vectorstore = self.ingester.get_vectorstore()
        
        # Get collection info
        try:
            collection = vectorstore._collection
            count = collection.count()
        except Exception:
            count = 0
        
        return {
            "initialized": self._initialized,
            "model_name": self.model_name,
            "temperature": self.temperature,
            "collection_name": self.settings.collection_name,
            "document_count": count,
            "persist_directory": self.settings.chroma_persist_directory,
        }
    
    def clear_collection(self) -> Dict[str, Any]:
        """
        Clear all documents from the collection.
        
        Returns:
            Dictionary with operation result
        """
        try:
            vectorstore = self.ingester.get_vectorstore()
            collection = vectorstore._collection
            
            # Delete all documents
            all_ids = collection.get()['ids']
            if all_ids:
                collection.delete(ids=all_ids)
            
            return {
                "success": True,
                "message": f"Cleared {len(all_ids)} documents from collection",
                "documents_deleted": len(all_ids)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error clearing collection: {str(e)}",
                "documents_deleted": 0
            }
    
    def list_supported_formats(self) -> List[str]:
        """
        Get list of supported document formats.
        
        Returns:
            List of supported file extensions
        """
        from ingest import DocumentLoaderFactory
        return DocumentLoaderFactory.get_supported_extensions()
