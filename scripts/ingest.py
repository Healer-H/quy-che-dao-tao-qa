#!/usr/bin/env python3
"""
Ingest PDF documents into the vector database
"""

import argparse
import os
import sys
import json
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import app modules
from app.rag.document_processor import DocumentProcessor
from app.rag.embeddings import EmbeddingsManager
from app.config import settings

def parse_args():
    parser = argparse.ArgumentParser(description="Ingest PDF documents into the vector database")
    parser.add_argument(
        "--pdf_dir", 
        type=str, 
        default=settings.RAW_DATA_DIR,
        help="Directory containing PDF files"
    )
    parser.add_argument(
        "--processed_dir", 
        type=str, 
        default=settings.PROCESSED_DATA_DIR,
        help="Directory to store processed documents"
    )
    parser.add_argument(
        "--vector_store_dir", 
        type=str, 
        default=settings.VECTOR_STORE_DIR,
        help="Directory to store vector database"
    )
    parser.add_argument(
        "--chunk_size", 
        type=int, 
        default=settings.CHUNK_SIZE,
        help="Size of text chunks"
    )
    parser.add_argument(
        "--chunk_overlap", 
        type=int, 
        default=settings.CHUNK_OVERLAP,
        help="Overlap between chunks"
    )
    parser.add_argument(
        "--embedding_model", 
        type=str, 
        default=settings.EMBEDDING_MODEL_NAME,
        help="Embedding model to use"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="Process a specific file (optional)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    print(f"🔍 Initializing document processor with chunk size {args.chunk_size} and overlap {args.chunk_overlap}")
    
    # Initialize document processor
    document_processor = DocumentProcessor(
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
        raw_dir=args.pdf_dir,
        processed_dir=args.processed_dir
    )
    
    print(f"🔤 Initializing embeddings manager with model {args.embedding_model}")
    
    # Initialize embeddings manager
    embeddings_manager = EmbeddingsManager(
        embedding_model_name=args.embedding_model,
        vector_store_path=args.vector_store_dir
    )
    
    # Process documents
    if args.file:
        if not os.path.exists(os.path.join(args.pdf_dir, args.file)):
            print(f"❌ File {args.file} not found in {args.pdf_dir}")
            return
        
        print(f"📄 Processing file: {args.file}")
        chunks = document_processor.process_pdf(args.file)
        
        if not chunks:
            print(f"❌ Failed to process {args.file}")
            return
        
        document_processor.save_chunks({args.file: chunks})
        
        print(f"✅ Processed {len(chunks)} chunks from {args.file}")
        print(f"💾 Saved chunks to {args.processed_dir}")
        
        print(f"🧠 Adding chunks to vector store")
        embeddings_manager.add_documents(chunks)
        
        print(f"✅ Added {len(chunks)} chunks to vector store")
    else:
        print(f"📚 Processing all PDF files in {args.pdf_dir}")
        
        all_chunks = document_processor.process_all_pdfs()
        
        if not all_chunks:
            print(f"❌ No PDF files found or failed to process files in {args.pdf_dir}")
            return
        
        document_processor.save_chunks(all_chunks)
        
        total_chunks = sum(len(chunks) for chunks in all_chunks.values())
        print(f"✅ Processed {total_chunks} chunks from {len(all_chunks)} files")
        print(f"💾 Saved chunks to {args.processed_dir}")
        
        print(f"🧠 Adding chunks to vector store")
        
        for doc_chunks in all_chunks.values():
            embeddings_manager.add_documents(doc_chunks)
        
        print(f"✅ Added {total_chunks} chunks to vector store")
    
    print("🎉 Done!")

if __name__ == "__main__":
    main()