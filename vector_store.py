import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List, Optional
import os
import tempfile
import shutil
import numpy as np

class SimpleEmbeddingFallback:
    """
    Simple fallback embedding class when sentence-transformers is not available.
    Uses basic TF-IDF style embeddings with LangChain interface.
    """
    def __init__(self):
        self.vocab = {}
        self.vocab_size = 0

    def embed_documents(self, texts):
        """Embed multiple documents - required by LangChain."""
        return self._encode_texts(texts)

    def embed_query(self, text):
        """Embed a single query - required by LangChain."""
        return self._encode_texts([text])[0]

    def _encode_texts(self, texts):
        """Internal encoding method."""
        embeddings = []
        for text in texts:
            # Simple word-based encoding
            words = text.lower().split()
            embedding = np.zeros(384)  # Standard embedding size

            for i, word in enumerate(words):
                if word not in self.vocab:
                    self.vocab[word] = self.vocab_size
                    self.vocab_size += 1

                # Simple positional encoding
                word_idx = self.vocab[word]
                pos = i / max(len(words), 1)
                embedding[word_idx % 384] += 1.0 * (1 - pos)

            # Normalize
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            embeddings.append(embedding.tolist())  # Convert to list for LangChain

        return embeddings

class VectorStoreManager:
    def __init__(self):
        """
        Initialize vector store manager with free sentence-transformers embeddings.
        """
        try:
            # Try to import sentence_transformers directly
            from sentence_transformers import SentenceTransformer
            self.embeddings = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        except ImportError:
            # Fallback: create a simple mock embedding class
            self.embeddings = SimpleEmbeddingFallback()

        # Use a temporary directory for ChromaDB persistence
        self.persist_directory = os.path.join(tempfile.gettempdir(), "website_chatbot_chroma")
        os.makedirs(self.persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

    def create_store(self, documents: List[Document]) -> Chroma:
        """
        Create a vector store from documents.

        Args:
            documents: List of Document objects with text chunks and metadata

        Returns:
            Chroma vector store instance
        """
        if not documents:
            raise ValueError("No documents provided for vector store creation")

        # Create a unique collection name based on source URL
        source_url = documents[0].metadata.get('source_url', 'unknown')
        collection_name = self._generate_collection_name(source_url)

        # Create vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            client=self.chroma_client,
            collection_name=collection_name,
            persist_directory=self.persist_directory
        )

        return vector_store

    def load_store(self, collection_name: str) -> Optional[Chroma]:
        """
        Load an existing vector store.

        Args:
            collection_name: Name of the collection to load

        Returns:
            Chroma vector store instance or None if not found
        """
        try:
            vector_store = Chroma(
                client=self.chroma_client,
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
            return vector_store
        except Exception:
            return None

    def similarity_search(self, vector_store: Chroma, query: str, k: int = 5) -> List[Document]:
        """
        Perform similarity search on the vector store.

        Args:
            vector_store: Chroma vector store instance
            query: Search query
            k: Number of results to return

        Returns:
            List of similar documents
        """
        return vector_store.similarity_search(query, k=k)

    def _generate_collection_name(self, source_url: str) -> str:
        """
        Generate a unique collection name from source URL.

        Args:
            source_url: Source URL

        Returns:
            Collection name safe for ChromaDB (only alphanumeric, dots, hyphens)
        """
        from urllib.parse import urlparse
        import re

        parsed = urlparse(source_url)
        domain = parsed.netloc

        # Clean domain: remove www. prefix, keep only valid chars
        if domain.startswith('www.'):
            domain = domain[4:]

        # Replace invalid characters with hyphens
        domain = re.sub(r'[^a-zA-Z0-9.-]', '-', domain)

        # Ensure it starts and ends with alphanumeric
        domain = re.sub(r'^[^a-zA-Z0-9]+', '', domain)
        domain = re.sub(r'[^a-zA-Z0-9]+$', '', domain)

        # Ensure minimum length and valid format
        if len(domain) < 3:
            domain = f"site-{domain or 'default'}"

        # Limit length
        return domain[:50]

    def clear_all_stores(self):
        """
        Clear all stored vector stores (for cleanup).
        """
        try:
            if os.path.exists(self.persist_directory):
                shutil.rmtree(self.persist_directory)
                os.makedirs(self.persist_directory, exist_ok=True)
        except Exception:
            pass  # Ignore cleanup errors
