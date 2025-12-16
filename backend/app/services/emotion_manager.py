import chromadb
from chromadb.utils import embedding_functions
from app.core.config import settings
import os

class EmotionManager:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "chroma_db"))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="avatar_emotions",
            embedding_function=self.embedding_function
        )

    def add_emotion(self, emotion_id: str, description: str, image_path: str, source: str = "pre-seeded"):
        self.collection.add(
            documents=[description],
            metadatas=[{"image_path": image_path, "source": source}],
            ids=[emotion_id]
        )

    def get_best_emotion(self, description: str, n_results: int = 1):
        results = self.collection.query(
            query_texts=[description],
            n_results=n_results
        )
        
        if results['ids'] and results['ids'][0]:
            # Return the best match
            return {
                "id": results['ids'][0][0],
                "distance": results['distances'][0][0] if 'distances' in results else 0,
                "metadata": results['metadatas'][0][0]
            }
        return None

emotion_manager = EmotionManager()
