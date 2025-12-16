import sys
import os
import chromadb
from app.core.config import settings

def reset_database():
    print("Resetting database collection...")
    try:
        client = chromadb.PersistentClient(path=os.path.join(settings.BASE_DIR, "chroma_db"))
        try:
            client.delete_collection("avatar_emotions")
            print("Collection 'avatar_emotions' deleted.")
        except ValueError:
            print("Collection 'avatar_emotions' does not exist.")
            
        print("Database reset complete.")
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
