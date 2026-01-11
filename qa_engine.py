from typing import List, Dict, Any
import os
import requests

class QAEngine:
    def __init__(self, vector_store):
        """
        Initialize QA engine with vector store using free alternatives.

        Args:
            vector_store: Chroma vector store instance
        """
        self.vector_store = vector_store

        # Try Groq API (free tier available)
        self.groq_api_key = os.getenv('GROQ_API_KEY', '')
        if self.groq_api_key:
            self.use_groq = True
        else:
            self.use_groq = False

    def ask_question(self, question: str, chat_history: List[Dict[str, str]] = None) -> str:
        """
        Ask a question and get an answer based on the website content.

        Args:
            question: The question to ask
            chat_history: Previous chat history (optional, used for context)

        Returns:
            Answer based on website content
        """
        try:
            # Retrieve relevant documents from vector store
            docs = self.vector_store.similarity_search(question, k=5)

            if not docs:
                return "The answer is not available on the provided website."

            # Extract context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in docs])

            # Build chat history for context
            messages = []
            if chat_history:
                for msg in chat_history[-6:]:  # Keep last 6 messages for context
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    if role == 'user':
                        messages.append({"role": "user", "content": content})
                    elif role == 'assistant':
                        messages.append({"role": "assistant", "content": content})

            # Add system message and current question
            system_message = """You are a helpful assistant that answers questions based ONLY on the provided website content.
If the answer to a question is not available in the provided context, respond EXACTLY with:
"The answer is not available on the provided website."

Do not use any external knowledge or make assumptions. Base your answer strictly on the information provided in the context."""

            messages.insert(0, {"role": "system", "content": system_message})
            messages.append({"role": "user", "content": f"Context from the website:\n{context}\n\nQuestion: {question}"})

            # Try Groq API first (free tier)
            if self.use_groq:
                try:
                    groq_response = requests.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama2-70b-4096",
                            "messages": messages,
                            "temperature": 0.1,
                            "max_tokens": 500
                        }
                    )
                    if groq_response.status_code == 200:
                        answer = groq_response.json()["choices"][0]["message"]["content"].strip()
                    else:
                        raise Exception("Groq API failed")
                except:
                    # Fallback to simple keyword matching
                    answer = self._simple_answer(question, context)
            else:
                # No API available, use simple keyword matching
                answer = self._simple_answer(question, context)

            # Ensure the response follows the required format
            if not answer or answer.lower().startswith("i don't know") or answer.lower().startswith("i'm sorry"):
                return "The answer is not available on the provided website."

            # Check if answer contains the exact required phrase
            if "the answer is not available on the provided website" in answer.lower():
                return "The answer is not available on the provided website."

            return answer

        except Exception as e:
            # In case of any error, return the standard message
            return "The answer is not available on the provided website."

    def _update_memory_from_history(self, chat_history: List[Dict[str, str]]):
        """
        Update conversation memory from chat history.

        Args:
            chat_history: List of chat messages with 'role' and 'content'
        """
        try:
            # Clear existing memory
            self.memory.clear()

            # Add chat history to memory
            for message in chat_history[-10:]:  # Keep last 10 messages for context
                role = message.get('role', '')
                content = message.get('content', '')

                if role == 'user':
                    # For memory, we need to store as human message
                    self.memory.chat_memory.add_user_message(content)
                elif role == 'assistant':
                    self.memory.chat_memory.add_ai_message(content)

        except Exception:
            # If memory update fails, continue without it
            pass

    def _simple_answer(self, question: str, context: str) -> str:
        """
        Provide a simple answer based on keyword matching when no LLM API is available.

        Args:
            question: The user's question
            context: Retrieved context from the website

        Returns:
            Simple answer based on keyword matching
        """
        question_lower = question.lower()
        context_lower = context.lower()

        # Basic keyword matching for common questions
        if any(word in question_lower for word in ['what is', 'what are', 'define', 'explain']):
            # Try to find relevant sentences containing key terms
            sentences = context.split('.')
            relevant_sentences = []

            # Extract key terms from question (remove question words)
            question_words = ['what', 'is', 'are', 'the', 'a', 'an', 'how', 'why', 'when', 'where', 'who']
            key_terms = [word for word in question_lower.split() if word not in question_words and len(word) > 2]

            for sentence in sentences:
                if any(term in sentence.lower() for term in key_terms[:3]):  # Use top 3 key terms
                    relevant_sentences.append(sentence.strip())

            if relevant_sentences:
                return '. '.join(relevant_sentences[:2]) + '.'  # Return up to 2 relevant sentences

        # For other types of questions, try to find any relevant content
        words = question_lower.split()
        content_words = [word for word in words if len(word) > 3]  # Focus on longer words

        if content_words:
            # Find sentences containing these words
            sentences = context.split('.')
            matching_sentences = []

            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in content_words):
                    matching_sentences.append(sentence.strip())

            if matching_sentences:
                return '. '.join(matching_sentences[:3]) + '.'  # Return up to 3 sentences

        # If no relevant content found
        return "The answer is not available on the provided website."

    def clear_memory(self):
        """Clear conversation memory."""
        pass  # No memory to clear in free version
