"""
RAG Chain implementation using LangGraph.
Implements State Graph for the retrieval-augmented generation pipeline.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from operator import add

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langgraph.graph import StateGraph, END

from nerthus_ai.core.config import get_settings, PromptsLoader
from nerthus_ai.rag.ingest import DocumentIngester


class RAGState(TypedDict):
    """State definition for RAG workflow."""
    question: str
    context: Sequence[Document]
    messages: Annotated[Sequence[BaseMessage], add]
    answer: str
    collection_filter: Optional[str]


class RAGChain:
    """
    RAG Chain implementation using LangGraph State Graph.
    """
    
    def __init__(
        self,
        model_name: str = None,
        temperature: float = None,
        top_k: int = None,
    ):
        """
        Initialize RAG chain.
        
        Args:
            model_name: OpenAI model name
            temperature: Model temperature
            top_k: Number of documents to retrieve
        """
        settings = get_settings()
        
        self.model_name = model_name or settings.model_name
        self.temperature = temperature or settings.temperature
        self.top_k = top_k or settings.top_k_results
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
        )
        
        # Initialize prompts loader
        self.prompts_loader = PromptsLoader(settings.prompts_file)
        self.prompts_loader.load_prompts()
        
        # Initialize document ingester
        self.ingester = DocumentIngester()
        
        # Build the state graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph for RAG."""
        workflow = StateGraph(RAGState)
        
        # Add nodes
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_answer)
        
        # Add edges
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    def _retrieve_documents(self, state: RAGState) -> RAGState:
        """
        Retrieve relevant documents from vector store.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with retrieved documents
        """
        question = state["question"]
        
        collection_filter = state.get("collection_filter")
        collection_name = collection_filter or self.ingester.collection_name

        # Get vector store
        vectorstore = self.ingester.get_vectorstore(collection_name=collection_name)
        
        # Retrieve relevant documents
        search_kwargs = {"k": self.top_k}
        if collection_filter:
            search_kwargs["filter"] = {"collection": collection_filter}
        retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
        
        documents = retriever.get_relevant_documents(question)
        
        return {
            **state,
            "context": documents,
        }
    
    def _generate_answer(self, state: RAGState) -> RAGState:
        """
        Generate answer using LLM with retrieved context.
        
        Args:
            state: Current RAG state
            
        Returns:
            Updated state with generated answer
        """
        question = state["question"]
        context = state.get("context", [])
        
        # Format context
        context_text = "\n\n".join([doc.page_content for doc in context])
        
        # Get system prompt
        system_prompt = self.prompts_loader.get_system_prompt("contextual")
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages", optional=True),
            ("human", "{question}"),
        ])
        
        # Format the prompt
        formatted_prompt = prompt.format_messages(
            context=context_text,
            question=question,
            messages=state.get("messages", [])
        )
        
        # Generate response
        response = self.llm.invoke(formatted_prompt)
        
        # Update messages
        new_messages = [
            HumanMessage(content=question),
            AIMessage(content=response.content),
        ]
        
        return {
            **state,
            "answer": response.content,
            "messages": new_messages,
        }
    
    def query(self, question: str, collection_filter: Optional[str] = None) -> dict:
        """
        Execute RAG query.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with answer and context
        """
        initial_state = {
            "question": question,
            "context": [],
            "messages": [],
            "answer": "",
            "collection_filter": collection_filter,
        }
        
        # Run the graph
        result = self.graph.invoke(initial_state)
        
        return {
            "question": question,
            "answer": result["answer"],
            "context": [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in result.get("context", [])
            ],
        }
    
    def stream_query(self, question: str, collection_filter: Optional[str] = None):
        """
        Execute RAG query with streaming.
        
        Args:
            question: User question
            
        Yields:
            State updates during execution
        """
        initial_state = {
            "question": question,
            "context": [],
            "messages": [],
            "answer": "",
            "collection_filter": collection_filter,
        }
        
        # Stream the graph execution
        for output in self.graph.stream(initial_state):
            yield output
