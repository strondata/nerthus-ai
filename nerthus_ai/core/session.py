"""
Session management module for Nerthus AI.
Implements Facade pattern for simplified session management.
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import date

from jinja2 import Environment, FileSystemLoader, select_autoescape
from langchain_openai import ChatOpenAI

from nerthus_ai.core.config import get_settings, Settings, PromptsLoader, DEFAULT_COLLECTION_NAME, TEMPLATES_DIR
from nerthus_ai.rag.extractors import parse_json_response
from nerthus_ai.rag.ingest import DocumentIngester
from nerthus_ai.rag.rag_chain import RAGChain


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
        default_collection = self.settings.collection_name
        if default_collection not in self.settings.available_collections:
            default_collection = DEFAULT_COLLECTION_NAME
        self.active_collection = default_collection
        
        # Initialize components
        self._ingester: Optional[DocumentIngester] = None
        self._rag_chain: Optional[RAGChain] = None
        self._prompts_loader: Optional[PromptsLoader] = None
        self._initialized = False
    
    @property
    def ingester(self) -> DocumentIngester:
        """Lazy initialization of document ingester."""
        if self._ingester is None:
            self._ingester = DocumentIngester(collection_name=self.active_collection)
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

    @property
    def prompts_loader(self) -> PromptsLoader:
        """Lazy initialization of prompts loader."""
        if self._prompts_loader is None:
            self._prompts_loader = PromptsLoader(self.settings.prompts_file)
            self._prompts_loader.load_prompts()
        return self._prompts_loader

    def set_context(self, collection_name: str) -> None:
        """
        Set active collection context for the session.
        """
        if collection_name not in self.settings.available_collections:
            raise ValueError(f"Coleção inválida: {collection_name}")
        self.active_collection = collection_name
        if self._ingester is not None:
            self._ingester.collection_name = collection_name
    
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
    
    def ingest_file(
        self,
        file_path: str,
        collection_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a single document file.
        
        Args:
            file_path: Path to the document file
            collection_name: Target collection name
            tags: Manual tags to attach to metadata
            
        Returns:
            Dictionary with ingestion results
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if collection_name:
            self.set_context(collection_name)

        chunks = self.ingester.ingest_file(
            file_path,
            collection_name=self.active_collection,
            tags=tags,
        )
        
        return {
            "success": True,
            "file": str(file_path),
            "chunks": chunks,
            "message": f"Successfully ingested {chunks} chunks from {file_path_obj.name}"
        }
    
    def ingest_directory(
        self,
        directory_path: str,
        collection_name: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
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
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")
        
        if collection_name:
            self.set_context(collection_name)

        results = self.ingester.ingest_directory(
            directory_path,
            collection_name=self.active_collection,
            tags=tags,
        )
        
        return {
            "success": True,
            "directory": str(directory_path),
            "total_files": results["total_files"],
            "total_chunks": results["total_chunks"],
            "files_processed": results["files_processed"],
            "errors": results["errors"],
            "message": f"Ingested {results['total_files']} files ({results['total_chunks']} chunks)"
        }
    
    def query(self, question: str, collection_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a RAG query.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and context
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        if collection_name:
            self.set_context(collection_name)

        result = self.rag_chain.query(
            question,
            collection_filter=self.active_collection,
        )
        
        return {
            "success": True,
            "question": question,
            "answer": result["answer"],
            "context": result["context"],
            "num_sources": len(result["context"])
        }
    
    def stream_query(self, question: str, collection_name: Optional[str] = None):
        """
        Execute a RAG query with streaming.
        
        Args:
            question: User question
            
        Yields:
            State updates during execution
        """
        if not question.strip():
            raise ValueError("Question cannot be empty")
        
        if collection_name:
            self.set_context(collection_name)

        yield from self.rag_chain.stream_query(
            question,
            collection_filter=self.active_collection,
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.
        
        Returns:
            Dictionary with session stats
        """
        vectorstore = self.ingester.get_vectorstore(collection_name=self.active_collection)
        
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
            "collection_name": self.active_collection,
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
            vectorstore = self.ingester.get_vectorstore(collection_name=self.active_collection)
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
        from nerthus_ai.rag.ingest import DocumentLoaderFactory
        return DocumentLoaderFactory.get_supported_extensions()

    def generate_report(
        self,
        report_type: str,
        filter_collection: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a technical report from the current collection.
        """
        collection_name = filter_collection or self.active_collection
        self.set_context(collection_name)

        templates_dir = TEMPLATES_DIR
        template_name = f"{report_type}.md"
        if not (templates_dir / template_name).exists():
            raise FileNotFoundError(f"Template not found: {template_name}")

        vectorstore = self.ingester.get_vectorstore(collection_name=collection_name)
        doc_count = 0
        documents = []
        context_limit = max(1, self.settings.report_context_documents)
        try:
            collection = vectorstore._collection
            doc_count = collection.count()
            payload = collection.get(
                include=["documents"],
                limit=context_limit,
            )
            documents = payload.get("documents", []) or []
        except Exception:
            documents = []
            doc_count = 0

        context_text = "\n\n".join(documents[:context_limit])
        report_data = {
            "llm_generated_process_summary": "",
            "formulations": [],
            "anomalies_list": "",
            "conclusion_text": "",
        }

        prompt = self.prompts_loader.get_template(f"{report_type}_prompt")
        if prompt and context_text:
            llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
            )
            response = llm.invoke(
                prompt.format(
                    context=context_text,
                    collection_name=collection_name,
                    doc_count=doc_count,
                )
            )
            content = response.content if hasattr(response, "content") else str(response)
            parsed = parse_json_response(content)
            if isinstance(parsed, dict):
                report_data["llm_generated_process_summary"] = parsed.get(
                    "llm_generated_process_summary",
                    report_data["llm_generated_process_summary"],
                )
                formulations = parsed.get("formulations")
                if isinstance(formulations, list):
                    report_data["formulations"] = formulations
                anomalies_list = parsed.get("anomalies_list")
                if isinstance(anomalies_list, list):
                    report_data["anomalies_list"] = ", ".join(
                        str(item) for item in anomalies_list
                    )
                elif isinstance(anomalies_list, str):
                    report_data["anomalies_list"] = anomalies_list
                report_data["conclusion_text"] = parsed.get(
                    "conclusion_text",
                    report_data["conclusion_text"],
                )

        env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(),
        )
        template = env.get_template(template_name)
        content = template.render(
            collection_name=collection_name,
            report_date=date.today().isoformat(),
            doc_count=doc_count,
            **report_data,
        )

        return {
            "success": True,
            "collection_name": collection_name,
            "report_type": report_type,
            "content": content,
        }
