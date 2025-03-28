from typing import List, Dict, Any
from app.rag.embeddings import EmbeddingsManager

class DocumentRetriever:
    """Retrieve relevant documents for a given query"""
    
    def __init__(self, embeddings_manager: EmbeddingsManager):
        self.embeddings_manager = embeddings_manager
    
    def retrieve_documents(
        self, 
        query: str, 
        k: int = 3,
        source_filter: str = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant documents for a query
        
        Args:
            query: User query
            k: Number of documents to retrieve
            source_filter: Optional filter by document source
            
        Returns:
            List of relevant document chunks with metadata
        """
        # Create filter if source is specified
        filter_dict = None
        if source_filter:
            filter_dict = {"source": source_filter}
        
        # Retrieve relevant documents
        documents = self.embeddings_manager.similarity_search(
            query=query,
            k=k,
            filter_metadata=filter_dict
        )
        
        return documents
    
    def format_retrieved_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents for context insertion"""
        context = ""
        
        for i, doc in enumerate(documents):
            source = doc["metadata"].get("source", "Unknown source")
            context += f"\n\nTRÍCH DẪN #{i+1} (Nguồn: {source}):\n{doc['text']}"
        
        return context