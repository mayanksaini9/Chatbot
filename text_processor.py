from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List, Dict, Any
import re

class TextProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize text processor with configurable chunk parameters.

        Args:
            chunk_size: Maximum size of each chunk
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_and_chunk(self, content_data: Dict[str, str], source_url: str) -> List[Document]:
        """
        Process extracted content and split into chunks with metadata.

        Args:
            content_data: Dictionary containing 'title', 'content', 'url'
            source_url: Source URL for metadata

        Returns:
            List of Document objects with text chunks and metadata
        """
        if not content_data or 'content' not in content_data:
            return []

        # Clean the text
        cleaned_text = self._clean_text(content_data['content'])

        if not cleaned_text.strip():
            return []

        # Create text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        # Split text into chunks
        chunks = text_splitter.split_text(cleaned_text)

        # Create Document objects with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'source_url': source_url,
                'page_title': content_data.get('title', 'Untitled Page'),
                'chunk_index': i,
                'total_chunks': len(chunks)
            }

            doc = Document(
                page_content=chunk.strip(),
                metadata=metadata
            )
            documents.append(doc)

        return documents

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove excessive newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Remove very short lines that might be artifacts
        lines = text.split('\n')
        filtered_lines = []
        for line in lines:
            line = line.strip()
            # Keep lines that are either long enough or contain important punctuation
            if len(line) >= 10 or re.search(r'[.!?]$', line):
                filtered_lines.append(line)

        text = '\n'.join(filtered_lines)

        return text.strip()

    def update_chunk_config(self, chunk_size: int, chunk_overlap: int):
        """
        Update chunk configuration parameters.

        Args:
            chunk_size: New chunk size
            chunk_overlap: New chunk overlap
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
