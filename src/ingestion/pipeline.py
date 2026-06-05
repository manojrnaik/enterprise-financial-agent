import os
from dotenv import load_dotenv
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader

load_dotenv()

class IngestionPipeline:
    def __init__(self):
        # Using text-embedding-3-small for cost efficiency and optimal dimensionality
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.text_splitter = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95
        )

    def process_pdf(self, file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Target document not found at: {file_path}")
            
        print(f"📦 Extracting text layout dynamically from: {file_path}")
        loader = PyMuPDFLoader(file_path)
        raw_docs = loader.load()
        
        print("🧠 Analyzing text semantic distances and calculating statistical splits...")
        semantic_chunks = self.text_splitter.split_documents(raw_docs)
        print(f"✅ Extracted {len(semantic_chunks)} logically sound chunks.")
        
        return semantic_chunks

if __name__ == "__main__":
    # Quick structural smoke test
    pipeline = IngestionPipeline()
    print("Ingestion engine initialized successfully.")
