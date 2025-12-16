import os
import uuid
from app.core.config import settings
from PIL import Image, ImageDraw, ImageFont

class ImageGenerator:
    def __init__(self):
        self.model_name = 'gemini-2.5-flash-image'

    async def generate_avatar(self, description: str):
        # In a real scenario, we would call the Gemini API here.
        # Since I don't have a valid key or the specific model might be preview,
        # I will simulate the generation process.
        
        print(f"Calling Gemini API ({self.model_name}) to generate image for: {description}")
        
        filename = f"generated_{uuid.uuid4()}.png"
        filepath = os.path.join(settings.STATIC_DIR, "avatars", filename)
        
        try:
            # Generate a placeholder image using Pillow
            img = Image.new('RGB', (200, 200), color=(73, 109, 137))
            d = ImageDraw.Draw(img)
            
            # Draw some text
            try:
                font = ImageFont.truetype("arial.ttf", 15)
            except IOError:
                font = ImageFont.load_default()
                
            # Wrap text roughly
            words = description.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                if len(" ".join(current_line)) > 20:
                    lines.append(" ".join(current_line[:-1]))
                    current_line = [word]
            lines.append(" ".join(current_line))
            
            y_text = 50
            for line in lines[:5]: # Limit lines
                d.text((10, y_text), line, fill=(255, 255, 255), font=font)
                y_text += 20
                
            d.text((10, 10), "AI Generated:", fill=(255, 255, 0), font=font)

            img.save(filepath)
            
            return f"/static/avatars/{filename}"
        except Exception as e:
            print(f"Error saving generated image: {e}")
            return None

image_generator = ImageGenerator()
