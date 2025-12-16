import sys
import os

# Add the current directory to sys.path to allow importing app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.emotion_manager import emotion_manager

# Dummy data for seeding
emotions = [
    {"id": "happy_01", "description": "a warm, friendly smile with happy eyes", "image_path": "/static/avatars/happy_01.png"},
    {"id": "sad_01", "description": "a sad expression with downcast eyes", "image_path": "/static/avatars/sad_01.png"},
    {"id": "confused_01", "description": "a confused look with furrowed brows", "image_path": "/static/avatars/confused_01.png"},
    {"id": "angry_01", "description": "an angry face with intense eyes", "image_path": "/static/avatars/angry_01.png"},
    {"id": "neutral_01", "description": "a neutral, calm expression", "image_path": "/static/avatars/neutral_01.png"},
]

def seed_emotions():
    print("Seeding emotions...")
    for emotion in emotions:
        emotion_manager.add_emotion(
            emotion_id=emotion["id"],
            description=emotion["description"],
            image_path=emotion["image_path"]
        )
    print("Seeding complete.")

if __name__ == "__main__":
    seed_emotions()
