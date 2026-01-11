# Website Chatbot with AI Embeddings

A Streamlit-based AI chatbot that crawls websites, creates embeddings from their content, and allows users to ask questions strictly related to the website content using retrieval-augmented generation (RAG).

## Features

- **Website Crawling**: Extracts meaningful content from websites while removing headers, footers, navigation, and advertisements
- **Text Processing**: Cleans and chunks text content with configurable parameters
- **Vector Embeddings**: Uses OpenAI embeddings to create semantic representations of content
- **Vector Storage**: Persists embeddings in ChromaDB for efficient similarity search
- **Conversational QA**: Answers questions based solely on website content with conversation memory
- **Streamlit UI**: Clean and intuitive web interface for easy interaction

## Architecture

The application follows a modular architecture with the following components:

1. **Web Crawler** (`crawler.py`): Handles website content extraction using BeautifulSoup
2. **Text Processor** (`text_processor.py`): Cleans and chunks text using LangChain's RecursiveCharacterTextSplitter
3. **Vector Store Manager** (`vector_store.py`): Manages embeddings creation and ChromaDB storage
4. **QA Engine** (`qa_engine.py`): Implements conversational retrieval-augmented generation with memory
5. **Streamlit App** (`app.py`): Provides the user interface and orchestrates all components

## Technologies Used

### Frameworks & Libraries
- **Streamlit**: Web application framework for the UI
- **LangChain**: Orchestration framework for LLM applications and RAG pipelines
- **ChromaDB**: Vector database for storing and retrieving embeddings
- **BeautifulSoup**: HTML parsing and content extraction
- **Requests**: HTTP client for web crawling

### AI Models
- **LLM**: Free tier options (Groq API) or fallback keyword-based system
  - **Why chosen**: Provides free access to LLM capabilities. Falls back to intelligent keyword matching when no API is available.
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (free, local)
  - **Why chosen**: High-quality free embeddings that run locally without API costs, excellent semantic understanding.

### Vector Database
- **ChromaDB**
  - **Why chosen**: Lightweight, easy to set up, supports persistence, and integrates well with LangChain. Good for development and small-scale production use.

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd website_chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (Optional):
Create a `.env` file in the project root. For the **FREE version**, no API keys are required!:

```bash
# Free version - no API keys needed!
# Optional: Add Groq API key for better LLM responses
# GROQ_API_KEY=your_groq_api_key_here
```

**Note**: The free version works without any API keys using intelligent keyword matching. For better responses, you can optionally add a Groq API key (free tier available).

## Usage

### Local Development
Run the Streamlit application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

### Deployment
The application can be deployed to Streamlit Cloud or any platform supporting Streamlit apps.

## How It Works

1. **URL Input**: User enters a website URL
2. **Crawling**: Application fetches and parses the webpage, extracting meaningful content
3. **Text Processing**: Content is cleaned and split into semantic chunks with metadata
4. **Embedding Creation**: Text chunks are converted to vector embeddings using OpenAI
5. **Storage**: Embeddings are stored in ChromaDB for efficient retrieval
6. **Question Answering**: User questions are embedded and matched against stored content
7. **Response Generation**: LLM generates answers based solely on retrieved website content

## Key Features

- **Content Grounding**: Answers are strictly based on website content only
- **Conversation Memory**: Maintains context across multiple questions in a session
- **Error Handling**: Graceful handling of invalid URLs, network issues, and empty content
- **Configurable Chunking**: Adjustable chunk size and overlap for different content types
- **Metadata Preservation**: Maintains source URL, page title, and chunk information

## API Response Format

When information is not available on the website, the system responds exactly with:
```
"The answer is not available on the provided website."
```

## Assumptions & Limitations

### Assumptions
- Websites are publicly accessible without authentication
- Content is primarily in HTML format
- OpenAI API access is available and properly configured
- Single-page crawling (main page only)

### Limitations
- Does not handle JavaScript-rendered content
- Limited to single-page crawling (no site-wide indexing)
- Requires OpenAI API key and credits
- Memory usage scales with website content size
- No support for non-text content (images, videos, etc.)

### Future Improvements
- **Multi-page crawling**: Implement recursive crawling for entire websites
- **Content type detection**: Support for PDFs, documentation sites, etc.
- **Alternative embeddings**: Support for open-source embedding models
- **Advanced chunking**: Semantic chunking based on content structure
- **Caching**: Implement response caching for frequently asked questions
- **Authentication**: Support for password-protected websites
- **Multi-language support**: Handle non-English content
- **Performance optimization**: Implement async processing and batch operations
- **Monitoring**: Add logging and performance metrics

## Project Structure

```
website_chatbot/
├── app.py                 # Main Streamlit application
├── crawler.py            # Website content extraction
├── text_processor.py     # Text cleaning and chunking
├── vector_store.py       # Embedding creation and storage
├── qa_engine.py          # Question answering with memory
├── utils.py              # Utility functions
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
└── README.md            # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built for the Humanli.ai AI/ML Engineer assignment
- Uses modern AI frameworks and best practices for RAG applications
- Designed to demonstrate practical implementation of retrieval-augmented generation
