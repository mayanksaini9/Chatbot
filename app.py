import streamlit as st
import os
from dotenv import load_dotenv
from crawler import WebsiteCrawler
from text_processor import TextProcessor
from vector_store import VectorStoreManager
from qa_engine import QAEngine

# Load environment variables
load_dotenv()

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'url_indexed' not in st.session_state:
    st.session_state.url_indexed = False

st.title("Website Chatbot with AI Embeddings")
st.markdown("Enter a website URL, index its content, and ask questions about it!")

# URL Input Section
st.header("1. Enter Website URL")
url = st.text_input("Website URL", placeholder="https://example.com")

if st.button("Index Website"):
    if not url:
        st.error("Please enter a valid URL")
    else:
        with st.spinner("Crawling and indexing website..."):
            try:
                # Crawl website
                crawler = WebsiteCrawler()
                content = crawler.crawl(url)

                if not content:
                    st.error("No content could be extracted from the website")
                    st.stop()

                # Process text
                processor = TextProcessor()
                chunks = processor.process_and_chunk(content, url)

                if not chunks:
                    st.error("No meaningful content chunks could be created")
                    st.stop()

                # Create embeddings and store
                vector_manager = VectorStoreManager()
                st.session_state.vector_store = vector_manager.create_store(chunks)

                st.session_state.url_indexed = True
                st.success(f"Successfully indexed website! Created {len(chunks)} content chunks.")

            except Exception as e:
                st.error(f"Error indexing website: {str(e)}")

# Chat Interface Section
if st.session_state.url_indexed:
    st.header("2. Ask Questions")

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the website..."):
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    qa_engine = QAEngine(st.session_state.vector_store)
                    response = qa_engine.ask_question(prompt, st.session_state.chat_history)

                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

                except Exception as e:
                    error_msg = f"Error generating response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

# Clear chat button
if st.session_state.chat_history:
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit, LangChain, and OpenAI embeddings*")
