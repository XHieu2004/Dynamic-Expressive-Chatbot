import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Dynamic Expressive Chatbot"
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    STATIC_DIR: str = os.path.join(BASE_DIR, "static")

settings = Settings()
