import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
import os
import uuid

class HistoryManager:
    def __init__(self):
        # Use a separate path for history as requested
        self.client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "chroma_history_db"))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="chat_history",
            embedding_function=self.embedding_function
        )

    def store_chat_history(self, session_id: str, question: str, answer: str):
        # Format similar to reference
        question_key = f"User: {question}"
        answer_key = f"AI: {answer}"
        full_exchange = f"{question_key}\n{answer_key}"
        
        # Store both Q and A as searchable documents, but link them via metadata
        self.collection.add(
            documents=[question_key, answer_key],
            metadatas=[
                {"session_id": session_id, "full_exchange": full_exchange, "type": "question"},
                {"session_id": session_id, "full_exchange": full_exchange, "type": "answer"}
            ],
            ids=[f"{uuid.uuid4()}_q", f"{uuid.uuid4()}_a"]
        )

    def retrieve_context(self, session_id: str, query: str, top_k: int = 3):
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where={"session_id": session_id}
        )
        
        # Use a set to deduplicate exchanges (in case both Q and A match the query)
        exchanges = set()
        if results['metadatas']:
            for meta_list in results['metadatas']:
                for meta in meta_list:
                    if 'full_exchange' in meta:
                        exchanges.add(meta['full_exchange'])
        
        return "\n\n".join(exchanges) if exchanges else None

    def retrieve_last_n(self, session_id: str, n: int = 3):
        # Fallback to get some recent history if no semantic match
        # Using empty query string as a "match all" heuristic similar to reference
        results = self.collection.query(
            query_texts=[""],
            n_results=n * 2, # *2 because we store Q and A separately
            where={"session_id": session_id}
        )
        
        exchanges = set()
        if results['metadatas']:
            for meta_list in results['metadatas']:
                for meta in meta_list:
                    if 'full_exchange' in meta:
                        exchanges.add(meta['full_exchange'])
                        
        if not exchanges:
            return "No prior questions. This is the start of the conversation."
            
        return "\n\n".join(list(exchanges)[-n:])

history_manager = HistoryManager()
