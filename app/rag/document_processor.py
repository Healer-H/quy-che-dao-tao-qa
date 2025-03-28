import os
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentProcessor:
    """Process PDF documents and chunk them for RAG system"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        raw_dir: str = "data/raw",
        processed_dir: str = "data/processed"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        
        # Create directories if they don't exist
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file"""
        text = ""
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {str(e)}")
            return ""

    def chunk_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata"""
        chunks = self.text_splitter.create_documents([text], [metadata or {}])
        return [{"text": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks]

    def process_pdf(self, pdf_filename: str) -> List[Dict[str, Any]]:
        """Process a PDF file and return chunked documents with metadata"""
        pdf_path = os.path.join(self.raw_dir, pdf_filename)
        
        # Extract metadata from filename
        doc_id = os.path.splitext(pdf_filename)[0]
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            return []
        
        # Create metadata
        metadata = {
            "source": pdf_filename,
            "document_id": doc_id,
        }
        
        # Chunk text
        chunks = self.chunk_text(text, metadata)
        
        # Add page numbers and chunk IDs
        for i, chunk in enumerate(chunks):
            chunk["metadata"]["chunk_id"] = f"{doc_id}_chunk_{i}"
        
        return chunks

    def process_all_pdfs(self) -> Dict[str, List[Dict[str, Any]]]:
        """Process all PDFs in the raw directory"""
        all_chunks = {}
        
        for filename in os.listdir(self.raw_dir):
            if filename.lower().endswith(".pdf"):
                print(f"Processing {filename}...")
                chunks = self.process_pdf(filename)
                if chunks:
                    all_chunks[filename] = chunks
        
        return all_chunks

    def save_chunks(self, chunks: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save processed chunks to disk"""
        import json
        
        for doc_name, doc_chunks in chunks.items():
            output_path = os.path.join(
                self.processed_dir, 
                f"{os.path.splitext(doc_name)[0]}_chunks.json"
            )
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(doc_chunks, f, ensure_ascii=False, indent=2)