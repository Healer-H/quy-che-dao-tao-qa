import os
from typing import List, Dict, Any, Optional
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingsManager:
    """Manage document embeddings and vector store"""
    
    def __init__(
        self,
        embedding_model_name: str = "keepitreal/vietnamese-sbert",
        vector_store_path: str = "data/vectorstore",
        collection_name: str = "university_regulations"
    ):
        self.vector_store_path = vector_store_path
        self.collection_name = collection_name
        
        # Create directory if it doesn't exist
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # Initialize embedding model
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        
        # Initialize vector store
        self.vector_store = self.get_or_create_vector_store()
    
    def get_or_create_vector_store(self):
        """Get existing vector store or create a new one"""
        try:
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=self.vector_store_path
            )
        except Exception as e:
            print(f"Error loading vector store: {str(e)}. Creating a new one.")
            return Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embedding_model,
                persist_directory=self.vector_store_path
            )
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store"""
        texts = [doc["text"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        self.vector_store.persist()
    
    def similarity_search(
        self, 
        query: str, 
        k: int = 3,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector store"""
        docs = self.vector_store.similarity_search(
            query=query,
            k=k,
            filter=filter_metadata
        )
        
        results = []
        for doc in docs:
            results.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "score": getattr(doc, "score", None)  # Some implementations provide score
            })
            
        return results