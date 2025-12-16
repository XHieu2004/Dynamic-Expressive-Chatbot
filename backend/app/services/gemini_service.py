import google.generativeai as genai
from app.core.config import settings
import json

if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        # Using gemini-1.5-flash as a stable alternative to the requested gemini-2.5-pro
        self.model_name = 'gemini-2.5-flash' 
        self.model = genai.GenerativeModel(self.model_name)

    async def generate_response(self, user_message: str, context: str = ""):
        if not settings.GEMINI_API_KEY:
            return {"reply_text": "Gemini API Key not configured.", "emotion_description": "neutral", "emotion_category": "neutral"}
            
        prompt = f"""
        You are a helpful chatbot. 
        
        Context from previous conversation:
        {context}
        
        Respond to the user's message.
        Also, describe the emotion that best fits your response.
        Classify the emotion into one of these categories: "happy", "sad", "angry", "confused", "neutral".
        
        Return the response in JSON format with keys: 
        - "reply_text": your response
        - "emotion_description": a detailed visual description
        - "emotion_category": one of ["happy", "sad", "angry", "confused", "neutral"]
        
        User message: {user_message}
        """
        
        try:
            # Force JSON response if supported by the model/API, or just prompt engineering
            # Gemini 1.5 supports response_mime_type="application/json"
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error generating response: {e}")
            return {"reply_text": "I'm having trouble thinking right now.", "emotion_description": "confused", "emotion_category": "confused"}

gemini_service = GeminiService()
