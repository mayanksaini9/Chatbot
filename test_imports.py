#!/usr/bin/env python3
"""
Simple test script to check if all imports work correctly.
"""

def test_basic_imports():
    """Test basic Python imports."""
    try:
        import streamlit as st
        print("✓ streamlit imported successfully")

        import requests
        print("✓ requests imported successfully")

        from bs4 import BeautifulSoup
        print("✓ beautifulsoup4 imported successfully")

        import os
        from dotenv import load_dotenv
        print("✓ python-dotenv imported successfully")

        print("\n✓ All basic imports successful!")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_langchain_imports():
    """Test LangChain related imports."""
    try:
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        print("✓ langchain text splitter imported successfully")

        from langchain_core.documents import Document
        print("✓ langchain core documents imported successfully")

        print("\n✓ LangChain imports successful!")
        return True
    except ImportError as e:
        print(f"✗ LangChain import error: {e}")
        return False

def test_ai_imports():
    """Test AI-related imports (may fail without proper installation)."""
    try:
        import chromadb
        print("✓ chromadb imported successfully")

        import sentence_transformers
        print("✓ sentence-transformers imported successfully")

        import openai
        print("✓ openai imported successfully")

        import tiktoken
        print("✓ tiktoken imported successfully")

        print("\n✓ All AI imports successful!")
        return True
    except ImportError as e:
        print(f"✗ AI import error: {e}")
        return False

if __name__ == "__main__":
    print("Testing imports for Website Chatbot...\n")

    basic_ok = test_basic_imports()
    print()
    langchain_ok = test_langchain_imports()
    print()
    ai_ok = test_ai_imports()

    print("\n" + "="*50)
    if basic_ok and langchain_ok:
        print("✓ Core functionality should work!")
        if ai_ok:
            print("✓ Full AI functionality available")
        else:
            print("⚠ AI functionality may require additional setup")
    else:
        print("✗ Core functionality has issues")

    print("="*50)
