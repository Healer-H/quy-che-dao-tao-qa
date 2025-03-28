from typing import Dict, List, Any, Optional
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from app.rag.retriever import DocumentRetriever

class RAGPipeline:
    """RAG pipeline for university regulation Q&A"""
    
    def __init__(
        self, 
        retriever: DocumentRetriever,
        model_name: str = "gpt-3.5-turbo",
        temperature: float = 0.1,
        max_tokens: int = 1024
    ):
        self.retriever = retriever
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Define RAG prompt template
        self.rag_template = """
        Bạn là trợ lý thông minh chuyên giải đáp về quy chế đào tạo của trường đại học. 
        Nhiệm vụ của bạn là trả lời câu hỏi dựa trên thông tin từ quy chế được cung cấp.
        
        THÔNG TIN QUY CHẾ:
        {context}
        
        CÂU HỎI: {question}
        
        HƯỚNG DẪN:
        1. Chỉ trả lời dựa trên thông tin từ quy chế được cung cấp.
        2. Nếu không có thông tin đủ để trả lời, hãy nói rõ bạn không tìm thấy thông tin liên quan.
        3. Trích dẫn chính xác các điều khoản, mục từ quy chế khi trả lời.
        4. Trả lời bằng ngôn ngữ dễ hiểu, mạch lạc.
        5. Không được tự ý thêm thông tin không có trong quy chế.
        
        TRẢ LỜI:
        """
        
        self.prompt = PromptTemplate(
            template=self.rag_template,
            input_variables=["context", "question"]
        )
    
    def generate_response(
        self, 
        query: str,
        k: int = 3,
        source_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response using RAG pipeline
        
        Args:
            query: User question
            k: Number of documents to retrieve
            source_filter: Optional filter by document source
            
        Returns:
            Dictionary with response and retrieved sources
        """
        # Retrieve relevant documents
        retrieved_docs = self.retriever.retrieve_documents(
            query=query,
            k=k,
            source_filter=source_filter
        )
        
        # Create context from retrieved documents
        context = self.retriever.format_retrieved_documents(retrieved_docs)
        
        # Generate response
        formatted_prompt = self.prompt.format(
            context=context,
            question=query
        )
        
        response = self.llm.invoke(formatted_prompt).content
        
        # Create response object
        return {
            "response": response,
            "sources": [
                {
                    "text": doc["text"],
                    "metadata": doc["metadata"]
                }
                for doc in retrieved_docs
            ]
        }