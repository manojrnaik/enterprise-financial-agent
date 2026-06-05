import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

class VectorStorageEngine:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.persist_directory = persist_directory

    def index_documents(self, documents):
        print(f"💾 Storing and building vector index inside: {self.persist_directory}")
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        print("🚀 Vector database successfully synchronized to disk.")
        return vector_store

    def get_retriever(self):
        vector_store = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        # Using Maximal Marginal Relevance (MMR) to maximize data diversity while eliminating redundancy
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 5, "fetch_k": 20}
        )
